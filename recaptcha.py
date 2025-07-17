# ABOUTME: reCAPTCHA client for verifying human submissions
# ABOUTME: Handles Google reCAPTCHA v3 token verification and scoring

import requests
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class RecaptchaClient:
    def __init__(self, secret_key: Optional[str] = None):
        self.secret = secret_key or os.environ.get("RECAPTCHA_SECRET_KEY")
        if not self.secret:
            raise ValueError("Missing RECAPTCHA_SECRET_KEY environment variable")
        
    def verify(self, token: str, ip: str) -> float:
        """Verify reCAPTCHA token and return score."""
        try:
            response = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": self.secret,
                    "response": token,
                    "remoteip": ip
                },
                timeout=10
            )
            result = response.json()
            
            if not result.get("success", False):
                error_codes = result.get("error-codes", [])
                raise ValueError(f"reCAPTCHA verification failed: {error_codes}")
                
            score = result.get("score", 0.0)
            return score
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"reCAPTCHA verification network error: {str(e)}")
        except Exception as e:
            raise ValueError(f"reCAPTCHA verification error: {str(e)}")