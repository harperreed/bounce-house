from flask import Flask, request, redirect
from prometheus_client import make_wsgi_app, Counter
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import tldextract
import validators
import logging
from urllib.parse import urlencode
from config import bounce_redirect_url, bounce_url, rate_limit

# Setup basic logging
logging.basicConfig(level=logging.INFO)

stat_name = "domain_counter"
stat_desc = "visits to domain"

domain_counter_stat = Counter(stat_name, stat_desc, ['domain'])

app = Flask(__name__)

# Use DispatcherMiddleware to dispatch to the Prometheus WSGI app on /metrics
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

# Rate limiting configuration
rate_limit_enabled = rate_limit["enabled"]
rate_limit_requests = rate_limit["requests"]
rate_limit_period = rate_limit["period"]

# In-memory store for rate limiting
rate_limit_store = {}


def get_client_ip() -> str:
    """Get the client's IP address from the request."""
    return request.remote_addr


def is_rate_limited(ip: str) -> bool:
    """Check if the given IP is rate-limited."""
    if not rate_limit_enabled:
        return False

    if ip not in rate_limit_store:
        rate_limit_store[ip] = []

    request_times = rate_limit_store[ip]
    current_time = time.time()

    # Remove outdated requests
    request_times = [t for t in request_times if current_time - t < rate_limit_period]
    rate_limit_store[ip] = request_times

    if len(request_times) >= rate_limit_requests:
        return True

    # Add the current request time
    request_times.append(current_time)
    return False


def sanitize_domain(domain: str) -> str:
    """Sanitize the domain parameter to prevent injection attacks."""
    return domain.replace("<", "").replace(">", "").replace("&", "").replace("\"", "").replace("'", "")


def extract_domain(host: str) -> str:
    """Extract and validate the domain from the Host header."""
    if not host:
        return ""

    extracted = tldextract.extract(host)
    domain = f"{extracted.domain}.{extracted.suffix}"

    if not validators.domain(domain):
        return ""

    return domain


@app.route('/')
def bounce():
    client_ip = get_client_ip()
    if is_rate_limited(client_ip):
        logging.warning(f"Rate limit exceeded for IP: {client_ip}")
        return "Rate limit exceeded. Please try again later.", 429

    # Extract the domain from the Host header
    domain = request.headers.get('Host', 'unknown')
    logging.info(f"Received request for domain: {domain}")

    # Default redirect URL in case of invalid domain
    redirect_url = bounce_url
    sanitized_domain = sanitize_domain(domain)
    extracted_domain = extract_domain(sanitized_domain)

    if extracted_domain:
        logging.info(f"Valid domain extracted: {extracted_domain}")
        domain_counter_stat.labels(extracted_domain).inc()
        redirect_url = f"{bounce_redirect_url}{urlencode({'domain': extracted_domain})}"
    else:
        logging.warning(f"Invalid domain: {domain}, redirecting to root.")
        domain_counter_stat.labels("root").inc()

    return redirect(redirect_url, code=301)
