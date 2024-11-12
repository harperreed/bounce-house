# Harper's Bounce House 🏠🔄

Welcome to the repository for Harper's Bounce House, a simple domain bouncer that redirects visitors to [harperrules.com](http://harperrules.com)! 🚀

## Summary of Project 📜

Harper's Bounce House is designed to handle incoming requests to various domains and redirect users accordingly. It enhances user experience by directing valid domains to specific URL parameters and managing invalid requests gracefully. The application also provides metrics via Prometheus to track the number of visits identified by domain. 

Key features of the project include:
- Validates incoming domain requests.
- Redirects users based on their domain.
- Tracks visits with Prometheus metrics.
- Implements rate limiting to prevent abuse.
- Sanitizes input for the domain parameter to enhance security.

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
    pip install -r requirements.txt
    ```

4. **Run the Application**:
    ```bash
    gunicorn bounce:app --bind 0.0.0.0:8080
    ```

5. **Access the Application**:
    Open your browser and navigate to `http://localhost:8080`.

6. **Deploy to Fly.io**:
    Use the `fly.toml` file to deploy the application on [Fly.io](https://fly.io/). Make sure to set up your Fly account and follow their deployment procedures.

## Tech Info 💻

### Technologies Used
- **Flask**: A micro web framework in Python that powers the application.
- **Gunicorn**: A Python WSGI HTTP Server for UNIX to serve the application.
- **Prometheus**: A metrics server to monitor application performance.
- **Validators**: Library to validate domain names.
- **TLD Extract**: Extracts the top-level domain from the incoming requests.

### Components
- `bounce.py`: Contains the core logic for domain bouncing and redirection.
- `config.py`: Contains configuration variables for the application.
- `Dockerfile`: Describes how to build a Docker image for the app.
- `fly.toml`: Configuration for deployment on Fly.io.
- `test_bounce.py`: Contains unit tests to ensure functionality.
- Workflow files in `.github/workflows/`: Includes CI/CD configuration for testing and linting.

### Metrics & Monitoring 📊
The application exposes Prometheus metrics at the `/metrics` endpoint, allowing for monitoring the domains being accessed and their respective visit counts.

## Contribution 🤝 
If you'd like to contribute to the Bounce House, feel free to open issues or submit pull requests. We welcome all contributions to make this project better! Let's bounce together! 🙌

Built with ❤️ by [@harperreed](https://github.com/harperreed)
