# ABOUTME: Test suite for the domain submission API
# ABOUTME: Tests form validation, spam protection, database operations, and endpoint behavior

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import tempfile
import os

from models import FormInput
from database import Repository
from recaptcha import RecaptchaClient
from airtable import AirtableClient
from submit import app


class TestFormInput:
    def test_valid_form_input(self):
        """Test valid form input validation."""
        form = FormInput(
            email="test@example.com",
            name="John Doe",
            budget=5000,
            domain_name="example.com",
            note="Test note"
        )
        assert form.email == "test@example.com"
        assert form.name == "John Doe"
        assert form.budget == 5000
        assert form.domain_name == "example.com"
        assert form.note == "Test note"
        assert form.hp_field is None

    def test_invalid_email(self):
        """Test invalid email validation."""
        with pytest.raises(ValueError):
            FormInput(
                email="invalid-email",
                name="John Doe",
                domain_name="example.com"
            )

    def test_invalid_name_characters(self):
        """Test name with invalid characters."""
        with pytest.raises(ValueError):
            FormInput(
                email="test@example.com",
                name="John123",
                domain_name="example.com"
            )

    def test_invalid_domain_format(self):
        """Test invalid domain format."""
        with pytest.raises(ValueError):
            FormInput(
                email="test@example.com",
                name="John Doe",
                domain_name="invalid-domain"
            )

    def test_domain_too_long(self):
        """Test domain name too long."""
        with pytest.raises(ValueError):
            FormInput(
                email="test@example.com",
                name="John Doe",
                domain_name="a" * 254 + ".com"
            )

    def test_honeypot_field(self):
        """Test honeypot field detection."""
        form = FormInput(
            email="test@example.com",
            name="John Doe",
            domain_name="example.com",
            hp_field="spam content"
        )
        assert form.hp_field == "spam content"


class TestRepository:
    def test_insert_new_submission(self):
        """Test inserting new submission."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            repo = Repository(f"sqlite:///{tmp.name}")
            
            form_data = FormInput(
                email="test@example.com",
                name="John Doe",
                domain_name="example.com"
            )
            
            meta = {
                "ip": "127.0.0.1",
                "user_agent": "TestAgent",
                "recaptcha_score": 0.9
            }
            
            result = repo.insert_if_new(form_data, meta)
            
            assert result["type"] == "inserted"
            assert result["submission"] is not None
            
            # Verify the submission was actually saved
            saved_submission = repo.get_submission_by_email("test@example.com")
            assert saved_submission is not None
            assert saved_submission.email == "test@example.com"
            
            # Cleanup
            os.unlink(tmp.name)

    def test_duplicate_submission(self):
        """Test duplicate email detection."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            repo = Repository(f"sqlite:///{tmp.name}")
            
            form_data = FormInput(
                email="test@example.com",
                name="John Doe",
                domain_name="example.com"
            )
            
            meta = {
                "ip": "127.0.0.1",
                "user_agent": "TestAgent",
                "recaptcha_score": 0.9
            }
            
            # First submission
            result1 = repo.insert_if_new(form_data, meta)
            assert result1["type"] == "inserted"
            
            # Second submission with same email
            result2 = repo.insert_if_new(form_data, meta)
            assert result2["type"] == "duplicate"
            
            # Cleanup
            os.unlink(tmp.name)


class TestRecaptchaClient:
    @patch('recaptcha.requests.post')
    def test_successful_verification(self, mock_post):
        """Test successful reCAPTCHA verification."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "score": 0.9
        }
        mock_post.return_value = mock_response
        
        client = RecaptchaClient("test_secret")
        score = client.verify("test_token", "127.0.0.1")
        
        assert score == 0.9
        mock_post.assert_called_once()

    @patch('recaptcha.requests.post')
    def test_failed_verification(self, mock_post):
        """Test failed reCAPTCHA verification."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": False,
            "error-codes": ["invalid-input-response"]
        }
        mock_post.return_value = mock_response
        
        client = RecaptchaClient("test_secret")
        
        with pytest.raises(ValueError) as exc_info:
            client.verify("invalid_token", "127.0.0.1")
        
        assert "reCAPTCHA verification failed" in str(exc_info.value)


class TestAirtableClient:
    @patch('airtable.requests.post')
    def test_successful_record_creation(self, mock_post):
        """Test successful Airtable record creation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "records": [{"id": "rec123456"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        client = AirtableClient("test_key", "test_base", "test_table")
        form_data = FormInput(
            email="test@example.com",
            name="John Doe",
            domain_name="example.com"
        )
        
        record_id = client.create_record(form_data)
        assert record_id == "rec123456"


class TestSubmitEndpoint:
    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    @patch('submit.get_recaptcha_client')
    @patch('submit.get_airtable_client')
    @patch('submit.get_repository')
    def test_successful_submission(self, mock_repo, mock_airtable, mock_recaptcha):
        """Test successful form submission."""
        # Setup mocks
        mock_recaptcha.return_value.verify.return_value = 0.9
        mock_repo.return_value.insert_if_new.return_value = {
            "type": "inserted",
            "submission": MagicMock()
        }
        mock_airtable.return_value.create_record.return_value = "rec123456"
        
        # Test data
        form_data = {
            "email": "test@example.com",
            "name": "John Doe",
            "domain_name": "example.com",
            "budget": 5000,
            "note": "Test note"
        }
        
        response = self.client.post(
            "/submit",
            json=form_data,
            params={"recaptcha_token": "test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["duplicate"] is False

    @patch('submit.get_recaptcha_client')
    def test_honeypot_detection(self, mock_recaptcha):
        """Test honeypot spam detection."""
        form_data = {
            "email": "test@example.com",
            "name": "John Doe",
            "domain_name": "example.com",
            "hp_field": "spam content"
        }
        
        response = self.client.post(
            "/submit",
            json=form_data,
            params={"recaptcha_token": "test_token"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["ok"] is False
        assert "Spam detected" in data["error"]

    @patch('submit.get_recaptcha_client')
    def test_low_recaptcha_score(self, mock_recaptcha):
        """Test low reCAPTCHA score rejection."""
        mock_recaptcha.return_value.verify.return_value = 0.3  # Low score
        
        form_data = {
            "email": "test@example.com",
            "name": "John Doe",
            "domain_name": "example.com"
        }
        
        response = self.client.post(
            "/submit",
            json=form_data,
            params={"recaptcha_token": "test_token"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["ok"] is False
        assert "reCAPTCHA verification failed" in data["error"]

    @patch('submit.get_recaptcha_client')
    @patch('submit.get_repository')
    def test_duplicate_submission(self, mock_repo, mock_recaptcha):
        """Test duplicate submission handling."""
        mock_recaptcha.return_value.verify.return_value = 0.9
        mock_repo.return_value.insert_if_new.return_value = {
            "type": "duplicate",
            "submission": MagicMock()
        }
        
        form_data = {
            "email": "test@example.com",
            "name": "John Doe",
            "domain_name": "example.com"
        }
        
        response = self.client.post(
            "/submit",
            json=form_data,
            params={"recaptcha_token": "test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["duplicate"] is True

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Domain Submission API" in data["message"]