# Deployment Guide

This document describes the deployment process for the Bounce House application using Fly.io.

## Overview

The application uses GitHub Actions for continuous deployment with the following workflow:

- **Production**: Automatic deployment to `bounce-house` app on `main` branch pushes
- **Preview**: Automatic preview deployments for pull requests
- **Cleanup**: Automatic cleanup of preview apps when PRs are closed

## GitHub Actions Workflow

The deployment workflow (`.github/workflows/fly.yml`) handles:

### Production Deployment
- Triggers on pushes to `main` branch
- Deploys to the production `bounce-house` app
- Uses `flyctl deploy --remote-only` for consistent builds

### PR Preview Deployment
- Triggers on PR open/update/reopen
- Creates a unique preview app: `bounce-house-pr-{PR_NUMBER}`
- Deploys the PR branch to the preview app
- Automatically comments on the PR with preview URLs
- Provides links to all endpoints (redirect, submit, health, metrics, docs)

### Cleanup
- Triggers when PR is closed
- Destroys the preview app to avoid resource waste
- Handles cases where app doesn't exist gracefully

## Required Secrets

Configure these secrets in your GitHub repository settings:

```
FLY_API_TOKEN - Your Fly.io API token
GITHUB_TOKEN - Automatically provided by GitHub Actions
```

## Environment Variables

The application requires these environment variables to be set in Fly.io:

```bash
# Set production secrets
fly secrets set RECAPTCHA_SECRET_KEY=your_recaptcha_secret_key
fly secrets set AIRTABLE_API_KEY=your_airtable_api_key
fly secrets set AIRTABLE_BASE_ID=your_airtable_base_id
fly secrets set AIRTABLE_TABLE_ID=your_airtable_table_id

# Optional: Set allowed origins for CORS
fly secrets set ALLOWED_ORIGINS="https://yourdomain.com,https://another-domain.com"
```

## Manual Deployment

For manual deployment or troubleshooting:

### Production
```bash
flyctl deploy --remote-only --app bounce-house
```

### Preview App
```bash
# Create and deploy a preview app
flyctl deploy --remote-only --app bounce-house-preview --config fly.toml

# Destroy when done
flyctl apps destroy bounce-house-preview --yes
```

## Application Structure

The deployed application runs as a single FastAPI app with these endpoints:

- `GET /` - Domain redirect service (original bounce functionality)
- `POST /submit` - Domain submission API with Airtable integration
- `GET /health` - Health check endpoint
- `GET /metrics` - Prometheus metrics endpoint
- `GET /api` - API information endpoint
- `GET /docs` - Interactive API documentation (FastAPI auto-generated)

## Monitoring

### Health Checks
- Health endpoint: `GET /health`
- Returns JSON with service status

### Metrics
- Prometheus metrics: `GET /metrics`
- Includes domain redirect counts and form submission metrics
- Compatible with existing Fly.io metrics configuration

### Logs
```bash
# Production logs
fly logs --app bounce-house

# Preview app logs
fly logs --app bounce-house-pr-123
```

## Troubleshooting

### Deployment Failures

1. **Check workflow logs**: Go to GitHub Actions tab in your repository
2. **Verify secrets**: Ensure `FLY_API_TOKEN` is set correctly
3. **Check Fly.io app**: Verify the app exists and you have permissions

### Environment Variable Issues

1. **Check secrets**: `fly secrets list --app bounce-house`
2. **Set missing secrets**: Use `fly secrets set KEY=value`
3. **Application logs**: Check for environment variable errors

### Preview App Issues

1. **App creation**: Preview apps are created automatically
2. **Resource limits**: Fly.io may have limits on number of apps
3. **Cleanup**: Old preview apps are automatically destroyed

## Configuration Files

### fly.toml
- Main Fly.io configuration
- Defines app name, regions, services, and health checks
- Used for both production and preview deployments

### Dockerfile
- Multi-stage build with `uv` package manager
- Optimized for Python applications
- Runs with `uvicorn` ASGI server

### .env.example
- Template for local development environment variables
- Copy to `.env` and fill in values for local testing

## Local Development

For local development with the same configuration:

1. Copy environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

2. Run the application:
   ```bash
   uv run python combined_app.py
   ```

3. Access endpoints:
   - Main app: http://localhost:8080
   - API docs: http://localhost:8080/docs
   - Health check: http://localhost:8080/health
   - Metrics: http://localhost:8080/metrics

## Security Notes

- Environment variables are handled securely via Fly.io secrets
- CORS is configured to allow specific origins
- Rate limiting is implemented for the submit endpoint
- reCAPTCHA v3 integration for spam protection
- Honeypot fields for additional spam detection

## Performance

- Single FastAPI application (no Flask/WSGI overhead)
- Efficient request handling with async/await
- Prometheus metrics for monitoring
- Health checks for reliability
- Optimized Docker build process