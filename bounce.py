from flask import Flask, request, redirect, render_template
from prometheus_client import make_wsgi_app, Counter
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import tldextract
import validators

stat_name = "domain_counter"
stat_desc = "visits to domain"

bounce_redirect_url = "http://harperrules.com/domain/?domain="
bounce_url = "http://harperrules.com/"

domain_counter_stat = Counter(stat_name, stat_desc, ['domain'])

app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

@app.route('/')
def bounce():
  domain = request.headers['Host']
  redirect_url = bounce_redirect_url + domain
  if validators.domain(domain):
    extracted = tldextract.extract(domain)
    domain = extracted.domain + "." + extracted.suffix
    domain_counter_stat.labels(domain).inc()
  else:
    domain_counter_stat.labels("root").inc()
    redirect_url = bounce_url
    
  return redirect(redirect_url, code=301)
  