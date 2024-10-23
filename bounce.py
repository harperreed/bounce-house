from flask import Flask, request, redirect, Response
from prometheus_client import make_wsgi_app, Counter
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import tldextract
import validators
import logging
from urllib.parse import quote
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


def extract_domain(host: str) -> str:
    if not host:
        logging.warning("Missing 'Host' header, using default domain 'unknown'")
        return 'unknown'
    extracted = tldextract.extract(host)
    domain = f"{extracted.domain}.{extracted.suffix}".lower()
    if not validators.domain(domain):
        logging.warning(f"Invalid domain: {domain}, using default domain 'unknown'")
        return 'unknown'
    return domain


def construct_redirect_url(domain: str) -> str:
    if domain == 'unknown':
        return bounce_url
    return f"{bounce_redirect_url}{quote(domain)}"


@app.route('/')
def bounce() -> Response:
    try:
        domain = extract_domain(request.headers.get('Host', 'unknown'))
        logging.info(f"Received request for domain: {domain}")
        domain_counter_stat.labels(domain).inc()
        redirect_url = construct_redirect_url(domain)
        return redirect(redirect_url, code=301)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return redirect(bounce_url, code=301)
