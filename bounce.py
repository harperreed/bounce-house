from flask import Flask, request, redirect
from prometheus_client import make_wsgi_app, Counter
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import tldextract
import validators
import logging

# Setup basic logging
logging.basicConfig(level=logging.DEBUG)

stat_name = "domain_counter"
stat_desc = "visits to domain"

bounce_redirect_url = "http://harperrules.com/domain/?domain="
bounce_url = "http://harperrules.com/"

domain_counter_stat = Counter(stat_name, stat_desc, ['domain', 'status'])

app = Flask(__name__)

# Use DispatcherMiddleware to dispatch to the Prometheus WSGI app on /metrics
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})


@app.route('/')
def bounce():
    try:
        # Extract the domain from the Host header
        domain = request.headers.get('Host', 'unknown')
        logging.debug(f"Received request for domain: {domain}")

        # Default redirect URL in case of invalid domain
        redirect_url = bounce_url
        if validators.domain(domain):
            extracted = tldextract.extract(domain)
            domain = f"{extracted.domain}.{extracted.suffix}"
            logging.debug(f"Valid domain extracted: {domain}")
            domain_counter_stat.labels(domain=domain, status='valid').inc()
            redirect_url = bounce_redirect_url + domain
        else:
            logging.warning(f"Invalid domain: {domain}, redirecting to root.")
            domain_counter_stat.labels(domain="root", status='invalid').inc()

        logging.debug(f"Redirecting to URL: {redirect_url}")
        return redirect(redirect_url, code=301)
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        domain_counter_stat.labels(domain="error", status='error').inc()
        return redirect(bounce_url, code=500)
