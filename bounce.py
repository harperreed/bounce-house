from flask import Flask, request, redirect, render_template
from prometheus_client import make_wsgi_app, Counter
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import tldextract
import validators

domain_counter_stat = Counter('counts', 'visits to domain', ['domain'])

app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

@app.route('/')
def bounce():
  domain = request.headers['Host']
  redirect_url = "http://harperrules.com/domain/?domain=" + domain
  if validators.domain(domain):
    extracted = tldextract.extract(domain)
    domain = extracted.domain + "." + extracted.suffix
    domain_counter_stat.labels(domain).inc()
  else:
    domain_counter_stat.labels("root").inc()
    redirect_url = "http://harperrules.com/"
    
  return redirect(redirect_url, code=301)
  