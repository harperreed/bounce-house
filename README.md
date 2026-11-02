# Harper's Bounce House 🏠🔄

Welcome to the repository for Harper's Bounce House, a simple domain bouncer that redirects visitors to [harperrules.com](http://harperrules.com)! 🚀

## Summary of Project 📜

Harper's Bounce House is a unified application that handles both domain redirection and domain submission requests. It enhances user experience by directing valid domains to specific URL parameters and managing invalid requests gracefully, while also providing a secure API for domain submission requests with Airtable integration.

Key features of the project include:
- **Domain Redirection**: Validates incoming domain requests and redirects users accordingly
- **Domain Submission API**: Secure endpoint for domain acquisition requests with spam protection
- **Airtable Integration**: Automatic syncing of submissions to Airtable
- **Spam Protection**: reCAPTCHA v3, honeypot fields, and rate limiting
- **Metrics & Monitoring**: Prometheus metrics for both redirect and submission tracking
- **Auto-deployment**: GitHub Actions workflows for production and PR preview deployments

## How to Use 🔧

To set up and run Harper's Bounce House locally, follow these steps:

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/harperreed/bounce-house.git
    cd bounce-house
    ```

2. **Create Virtual Environment (optional)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies**:
    Make sure you have [Python](https://www.python.org/downloads/) 3.13 or later installed. Then, run:
    ```bash
    uv sync  # or pip install -r requirements.txt
    ```

4. **Set up Environment Variables**:
    ```bash
    cp .env.example .env
    # Edit .env file with your API keys and configuration
    ```

5. **Run the Application**:
    ```bash
    uv run python combined_app.py
    ```

6. **Access the Application**:
    - Domain redirects: `http://localhost:8080/`
    - Submit API: `http://localhost:8080/submit`
    - Health check: `http://localhost:8080/health`
    - Metrics: `http://localhost:8080/metrics`
    - API docs: `http://localhost:8080/docs`

## Deployment 🚀

### Automatic Deployment
The application uses GitHub Actions for automatic deployment:
- **Production**: Deploys to `bounce-house` app on pushes to `main` branch
- **Preview**: Creates preview apps for pull requests (`bounce-house-pr-{number}`)
- **Cleanup**: Automatically destroys preview apps when PRs are closed

### Manual Deployment
1. **Set up Fly.io secrets**:
    ```bash
    ./setup-fly-secrets.sh
    ```

2. **Deploy manually**:
    ```bash
    flyctl deploy --remote-only
    ```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Tech Info 💻

### Technologies Used
- **FastAPI**: Modern, fast web framework for building APIs with Python
- **Uvicorn**: Lightning-fast ASGI server for Python applications
- **SQLAlchemy**: SQL toolkit and ORM for Python
- **Pydantic**: Data validation and settings management using Python type hints
- **Prometheus**: Metrics server to monitor application performance
- **Validators**: Library to validate domain names
- **TLD Extract**: Extracts the top-level domain from incoming requests
- **reCAPTCHA v3**: Google's spam protection service
- **Airtable**: Cloud-based database for storing submissions

### Components
- `combined_app.py`: Main application combining domain redirect and submission API
- `bounce.py`: Legacy Flask-based domain bouncing logic
- `submit.py`: Standalone FastAPI submission endpoint
- `models.py`: Pydantic models for form validation
- `database.py`: SQLAlchemy models and database operations
- `recaptcha.py`: reCAPTCHA v3 integration
- `airtable.py`: Airtable API client
- `middleware.py`: Rate limiting and spam protection
- `metrics.py`: Prometheus metrics definitions
- `Dockerfile`: Multi-stage Docker build configuration
- `fly.toml`: Fly.io deployment configuration
- `test_*.py`: Comprehensive test suites
- Workflow files in `.github/workflows/`: CI/CD for testing, linting, and deployment

### API Endpoints 🔗
- **GET /** - Domain redirect service (original bounce functionality)
- **POST /submit** - Domain submission API with spam protection
- **GET /health** - Health check endpoint
- **GET /metrics** - Prometheus metrics endpoint
- **GET /api** - API information endpoint
- **GET /docs** - Interactive API documentation

### Metrics & Monitoring 📊
The application exposes comprehensive Prometheus metrics at the `/metrics` endpoint:
- **Domain redirects**: Track visits by domain
- **Form submissions**: Monitor submission rates and success/failure
- **Spam detection**: Track honeypot hits and reCAPTCHA failures
- **Airtable sync**: Monitor API sync success rates
- **Rate limiting**: Track rate limit violations

## Contribution 🤝 
If you'd like to contribute to the Bounce House, feel free to open issues or submit pull requests. We welcome all contributions to make this project better! Let's bounce together! 🙌

Built with ❤️ by [@harperreed](https://github.com/harperreed)
