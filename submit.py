# ABOUTME: Main FastAPI application with /submit endpoint for domain submissions
# ABOUTME: Handles form processing, validation, spam protection, and Airtable syncing

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from typing import Optional

from models import FormInput
from database import Repository
from recaptcha import RecaptchaClient
from airtable import AirtableClient
from middleware import RateLimitMiddleware
from metrics import (
    FORM_SUBMISSIONS, FORM_SUBMISSIONS_SUCCESS, FORM_SUBMISSIONS_DUPLICATE,
    SPAM_DETECTION, RECAPTCHA_VERIFICATIONS, RECAPTCHA_SCORE,
    AIRTABLE_SYNC_ATTEMPTS, AIRTABLE_SYNC_SUCCESS, AIRTABLE_SYNC_FAILURES
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("domainer_submit")

# Initialize FastAPI app
app = FastAPI(title="Domain Submission API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware, max_requests=5, window_seconds=3600)

# Global instances - initialized lazily
repository = None
recaptcha_client = None
airtable_client = None


def get_repository():
    """Get repository instance."""
    global repository
    if repository is None:
        repository = Repository()
    return repository


def get_recaptcha_client():
    """Get reCAPTCHA client instance."""
    global recaptcha_client
    if recaptcha_client is None:
        recaptcha_client = RecaptchaClient()
    return recaptcha_client


def get_airtable_client():
    """Get Airtable client instance."""
    global airtable_client
    if airtable_client is None:
        airtable_client = AirtableClient()
    return airtable_client


def get_client_ip(request: Request) -> str:
    """Extract client IP from request headers."""
    # Try various headers in order of preference
    ip_headers = ["x-forwarded-for", "x-real-ip", "cf-connecting-ip"]
    
    for header in ip_headers:
        if header in request.headers:
            # For X-Forwarded-For, take the first IP (original client)
            return request.headers[header].split(",")[0].strip()
            
    # Fall back to client host
    return request.client.host if request.client else "unknown"


@app.post("/submit")
async def submit_domain(
    request: Request,
    form_data: FormInput,
    recaptcha_token: str
):
    """Handle domain submission with spam protection and Airtable sync."""
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "")
    
    logger.info(f"Processing form submission from {client_ip}, email: {form_data.email}")
    FORM_SUBMISSIONS.inc()
    
    # Check honeypot field
    if form_data.hp_field:
        SPAM_DETECTION.labels(detection_type="honeypot").inc()
        logger.warning(f"Honeypot field filled by {client_ip}")
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": "Spam detected"}
        )
    
    # Verify reCAPTCHA
    try:
        score = get_recaptcha_client().verify(recaptcha_token, client_ip)
        RECAPTCHA_SCORE.observe(score)
        logger.info(f"reCAPTCHA score: {score} for {client_ip}")
        
        if score < 0.5:
            RECAPTCHA_VERIFICATIONS.labels(result="failure").inc()
            SPAM_DETECTION.labels(detection_type="recaptcha_score").inc()
            logger.warning(f"Low reCAPTCHA score ({score}) from {client_ip}")
            return JSONResponse(
                status_code=400,
                content={"ok": False, "error": "reCAPTCHA verification failed"}
            )
        
        RECAPTCHA_VERIFICATIONS.labels(result="success").inc()
            
    except Exception as e:
        RECAPTCHA_VERIFICATIONS.labels(result="error").inc()
        logger.error(f"reCAPTCHA verification error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": "reCAPTCHA verification failed"}
        )
    
    # Save to database
    try:
        meta = {
            "ip": client_ip,
            "user_agent": user_agent,
            "recaptcha_score": score
        }
        
        result = get_repository().insert_if_new(form_data, meta)
        
        if result["type"] == "duplicate":
            FORM_SUBMISSIONS_DUPLICATE.inc()
            logger.info(f"Duplicate submission for email: {form_data.email}")
            return JSONResponse(
                status_code=200,
                content={"ok": True, "duplicate": True}
            )
        
        # New submission - sync to Airtable
        FORM_SUBMISSIONS_SUCCESS.inc()
        logger.info(f"New submission saved for email: {form_data.email}")
        
        try:
            AIRTABLE_SYNC_ATTEMPTS.inc()
            airtable_record_id = get_airtable_client().create_record(form_data)
            AIRTABLE_SYNC_SUCCESS.inc()
            logger.info(f"Synced to Airtable with ID: {airtable_record_id}")
        except Exception as e:
            # Don't fail the request if Airtable sync fails
            AIRTABLE_SYNC_FAILURES.inc()
            logger.error(f"Airtable sync failed: {str(e)}")
            
        return JSONResponse(
            status_code=200,
            content={"ok": True, "duplicate": False}
        )
        
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": "Internal server error"}
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "domain-submission-api"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Domain Submission API",
        "version": "1.0.0",
        "endpoints": {
            "submit": "POST /submit - Submit domain request",
            "health": "GET /health - Health check"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)