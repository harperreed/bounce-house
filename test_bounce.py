import pytest
from bounce import app, domain_counter_stat
from unittest.mock import patch


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_valid_domain_redirection(client):
    response = client.get('/', headers={'Host': 'example.com'})
    assert response.status_code == 301
    assert response.headers['Location'] == (
        'http://harperrules.com/domain/?domain=example.com'
    )


def test_invalid_domain_redirection(client):
    response = client.get('/', headers={'Host': 'invalid_domain'})
    assert response.status_code == 301
    assert response.headers['Location'] == 'http://harperrules.com/'


def test_missing_host_header(client):
    response = client.get('/')
    assert response.status_code == 301
    assert response.headers['Location'] == 'http://harperrules.com/'


def test_prometheus_counter_increment(client):
    with patch.object(domain_counter_stat, 'labels') as mock_labels:
        response = client.get('/', headers={'Host': 'example.com'})
        assert response.status_code == 301
        mock_labels.assert_called_once_with('example.com')
        mock_labels.return_value.inc.assert_called_once()


def test_rate_limiting(client):
    for _ in range(101):  # Assuming rate limit is 100
        response = client.get('/', headers={'Host': 'example.com'})
    assert response.status_code == 429  # Too Many Requests
