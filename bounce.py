from flask import Flask, request, redirect, render_template
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import validators
from prometheus_client import make_wsgi_app, Counter

domains_stat_name = "domain_visit"
domains_stat_description = "visits to domains"
domains_count = Counter(domains_stat_name, domains_stat_description)

app = Flask(__name__)

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

@app.route('/')
def bounce():
  domain = request.headers['Host']
  redirect_url = "http://harperrules.com/domain/?domain=" + domain
  if validators.domain(domain):
    stat_name = "domain_"+domain.replace(".","_")
    stat_description = "visits to domain: " + domain
    domain_count = Counter(stat_name, stat_description)
    domain_count.inc()
    domains_count.inc()
  else:
    stat_name = "root_request"
    stat_description = "request of root with no domain"
    root_count = Counter(stat_name, stat_description)
    root_count.inc()
    # return render_template('landing.html')
    redirect_url = "http://harperrules.com/"
    
  return redirect(redirect_url, code=301)
  