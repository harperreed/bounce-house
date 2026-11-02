# ABOUTME: Prometheus metrics for monitoring domain submission API
# ABOUTME: Tracks submission counts, validation errors, and spam detection metrics

from prometheus_client import Counter, Histogram, Gauge

# Form submission metrics
FORM_SUBMISSIONS = Counter("form_submissions_total", "Total form submissions processed")
FORM_SUBMISSIONS_SUCCESS = Counter("form_submissions_success_total", "Successful form submissions")
FORM_SUBMISSIONS_DUPLICATE = Counter("form_submissions_duplicate_total", "Duplicate form submissions")
VALIDATION_ERRORS = Counter("form_validation_errors_total", "Form validation errors", ["error_type"])
SPAM_DETECTION = Counter("spam_detection_triggers_total", "Spam detection triggers", ["detection_type"])

# reCAPTCHA metrics
RECAPTCHA_VERIFICATIONS = Counter("recaptcha_verifications_total", "reCAPTCHA verifications", ["result"])
RECAPTCHA_SCORE = Histogram("recaptcha_score", "Distribution of reCAPTCHA scores")

# Airtable sync metrics
AIRTABLE_SYNC_ATTEMPTS = Counter("airtable_sync_attempts_total", "Airtable sync attempts")
AIRTABLE_SYNC_SUCCESS = Counter("airtable_sync_success_total", "Successful Airtable syncs")
AIRTABLE_SYNC_FAILURES = Counter("airtable_sync_failures_total", "Failed Airtable syncs")

# Rate limiting metrics
RATE_LIMIT_HITS = Counter("rate_limit_hits_total", "Rate limit violations")

# Database metrics
DB_OPERATIONS = Counter("db_operations_total", "Database operations", ["operation"])
DB_ERRORS = Counter("db_errors_total", "Database errors")