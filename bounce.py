from flask import Flask, request, redirect
from prometheus_client import make_wsgi_app, Counter
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import tldextract
import validators
import logging
from urllib.parse import quote
from typing import Tuple
from config import Config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
config = Config()

# Setup rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

domain_counter_stat = Counter(config.STAT_NAME, config.STAT_DESC, ['domain'])

# Use DispatcherMiddleware to dispatch to the Prometheus WSGI app on /metrics
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

def extract_and_validate_domain(host: str) -> Tuple[str, bool]:
    """
    Extract and validate the domain from the host.

    Args:
        host (str): The host header from the request.

    Returns:
        Tuple[str, bool]: The extracted domain and a boolean indicating if it's valid.
    """
    if not host or host == 'unknown':
        logger.warning("Missing or unknown host header")
        return '', False

    if not validators.domain(host):
        logger.warning(f"Invalid domain: {host}")
        return '', False

    extracted = tldextract.extract(host)
    domain = f"{extracted.domain}.{extracted.suffix}"
    logger.info(f"Valid domain extracted: {domain}")
    return domain, True

def construct_redirect_url(domain: str) -> str:
    """
    Construct the redirect URL for a given domain.

    Args:
        domain (str): The validated domain.

    Returns:
        str: The constructed redirect URL.
    """
    return f"{config.BOUNCE_REDIRECT_URL}{quote(domain)}"

@app.route('/')
@limiter.limit("10/minute")
def bounce():
    host = request.headers.get('Host', 'unknown')
    logger.info(f"Received request for host: {host}")

    domain, is_valid = extract_and_validate_domain(host)

    if is_valid:
        domain_counter_stat.labels(domain).inc()
        redirect_url = construct_redirect_url(domain)
    else:
        domain_counter_stat.labels("root").inc()
        redirect_url = config.BOUNCE_URL

    return redirect(redirect_url, code=301)

if __name__ == '__main__':
    app.run(debug=config.DEBUG)
