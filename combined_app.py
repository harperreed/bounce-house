# ABOUTME: Combined application running both bounce redirects and submit API
# ABOUTME: Integrates Flask bouncer with FastAPI submit endpoint using FastAPI's mount feature

from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from prometheus_client import make_wsgi_app
from bounce import app as flask_app
from submit import app as submit_app

# Create main FastAPI app
app = FastAPI(title="Bounce House - Combined API")

# Mount the submit API at /api
app.mount("/api", submit_app)

# Mount the Flask bouncer at root (this handles domain redirects)
app.mount("/", WSGIMiddleware(flask_app))

# Expose metrics at /metrics (from the submit app)
app.mount("/metrics", WSGIMiddleware(make_wsgi_app()))

if __name__ == "__main__":
    import uvicorn
    print("Starting combined Bounce House application...")
    print("Domain redirects: http://localhost:8000/")
    print("Submit API: http://localhost:8000/api/submit")
    print("Metrics: http://localhost:8000/metrics")
    print("API docs: http://localhost:8000/api/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)