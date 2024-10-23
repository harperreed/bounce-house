import unittest
from unittest.mock import patch
from bounce import app, extract_and_validate_domain, construct_redirect_url
from config import Config


class TestBounce(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_extract_and_validate_domain_valid(self):
        domain, is_valid = extract_and_validate_domain("example.com")
        self.assertEqual(domain, "example.com")
        self.assertTrue(is_valid)

    def test_extract_and_validate_domain_invalid(self):
        domain, is_valid = extract_and_validate_domain("invalid_domain")
        self.assertEqual(domain, "")
        self.assertFalse(is_valid)

    def test_construct_redirect_url(self):
        url = construct_redirect_url("example.com")
        self.assertEqual(url, f"{Config().BOUNCE_REDIRECT_URL}example.com")

    @patch("bounce.domain_counter_stat")
    def test_bounce_valid_domain(self, mock_counter):
        response = self.app.get("/", headers={"Host": "example.com"})
        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response.location, f"{Config().BOUNCE_REDIRECT_URL}example.com"
        )
        mock_counter.labels.assert_called_once_with("example.com")
        mock_counter.labels().inc.assert_called_once()

    @patch("bounce.domain_counter_stat")
    def test_bounce_invalid_domain(self, mock_counter):
        response = self.app.get("/", headers={"Host": "invalid_domain"})
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.location, Config().BOUNCE_URL)
        mock_counter.labels.assert_called_once_with("root")
        mock_counter.labels().inc.assert_called_once()

    def test_metrics_endpoint(self):
        response = self.app.get("/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertIn("domain_counter", response.data.decode())

    @patch("bounce.limiter")
    def test_rate_limiting(self, mock_limiter):
        mock_limiter.limit.return_value = lambda x: x
        for _ in range(11):
            response = self.app.get("/", headers={"Host": "example.com"})
        self.assertEqual(response.status_code, 429)


if __name__ == "__main__":
    unittest.main()
