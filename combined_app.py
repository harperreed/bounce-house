# ABOUTME: Combined application running both bounce redirects and submit API
# ABOUTME: Integrates Flask bouncer with FastAPI submit endpoint for unified Fly.io deployment

import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request

# Load environment variables from .env file
load_dotenv()
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import RedirectResponse
from prometheus_client import make_wsgi_app
import tldextract
import validators
import logging

# Import the submit app components
from submit import (
    get_repository, get_recaptcha_client, get_airtable_client,
    get_client_ip, FormInput, 
    FORM_SUBMISSIONS, FORM_SUBMISSIONS_SUCCESS, FORM_SUBMISSIONS_DUPLICATE,
    SPAM_DETECTION, RECAPTCHA_VERIFICATIONS, RECAPTCHA_SCORE,
    AIRTABLE_SYNC_ATTEMPTS, AIRTABLE_SYNC_SUCCESS, AIRTABLE_SYNC_FAILURES
)
from middleware import RateLimitMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bounce_house")

# Create main FastAPI app
app = FastAPI(title="Bounce House - Combined API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add rate limiting middleware for submit endpoint
app.add_middleware(RateLimitMiddleware, max_requests=5, window_seconds=3600)

# Bounce configuration
bounce_redirect_url = "http://harperreed.com/domain/?domain="
bounce_url = "http://harperreed.com/"

# Prometheus metrics for bounce functionality
from prometheus_client import Counter
domain_counter_stat = Counter("domain_counter", "visits to domain", ['domain'])

# Mount metrics endpoint
app.mount("/metrics", WSGIMiddleware(make_wsgi_app()))

@app.get("/")
async def bounce_redirect(request: Request):
    """Handle domain redirects (original bounce functionality)."""
    # Extract the domain from the Host header
    domain = request.headers.get('Host', 'unknown')
    logger.info(f"Received request for domain: {domain}")

    # Default redirect URL in case of invalid domain
    redirect_url = bounce_url
    if validators.domain(domain):
        extracted = tldextract.extract(domain)
        domain = f"{extracted.domain}.{extracted.suffix}"
        logger.info(f"Valid domain extracted: {domain}")
        domain_counter_stat.labels(domain).inc()
        redirect_url = bounce_redirect_url + domain
    else:
        logger.warning(f"Invalid domain: {domain}, redirecting to root.")
        domain_counter_stat.labels("root").inc()

    return RedirectResponse(url=redirect_url, status_code=301)

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
    return {"status": "healthy", "service": "bounce-house-combined"}

@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "message": "Bounce House - Combined API",
        "version": "1.0.0",
        "endpoints": {
            "bounce": "GET / - Domain redirect service",
            "submit": "POST /submit - Submit domain request",
            "health": "GET /health - Health check",
            "metrics": "GET /metrics - Prometheus metrics"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    print("Starting combined Bounce House application...")
    print(f"Domain redirects: http://localhost:{port}/")
    print(f"Submit API: http://localhost:{port}/submit")
    print(f"Metrics: http://localhost:{port}/metrics")
    print(f"Health: http://localhost:{port}/health")
    uvicorn.run(app, host="0.0.0.0", port=port)