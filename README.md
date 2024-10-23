# Harper's Bounce House 🏠🔄

Welcome to the repository for Harper's Bounce House, a simple domain bouncer that redirects visitors to [harperrules.com](http://harperrules.com)! 🚀

## Repository Overview 📂

This repository contains the following files:

- `Procfile`: Specifies the command to run the application using Gunicorn.
- `README.md`: You're reading it right now! 📖
- `bounce.py`: The main Python script that handles the domain bouncing logic. 🐍
- `config.py`: Configuration file for the application. 🔧
- `test_bounce.py`: Unit and integration tests for the application. 🧪
- `fly.toml`: Configuration file for deploying the application on Fly.io. ☁️
- `requirements.txt`: Lists the Python dependencies required to run the application. 📜

## How It Works 🤔

When a user visits a domain that points to this application, the following steps occur:

1. The application extracts the domain from the `Host` header of the incoming request. 🔍
2. The domain is validated using the `validators` library. ✅
3. If the domain is valid, it extracts the domain name and suffix using `tldextract`. 🧐
4. The application increments a Prometheus counter for the specific domain. 📈
5. The user is redirected to `http://harperrules.com/domain/?domain=<extracted_domain>`. 🔀
6. If the domain is invalid, the user is redirected to the root URL `http://harperrules.com/`. 🚫

## New Features and Improvements 🆕

- Improved error handling and logging. 🛠️
- Type hints for better code readability and maintainability. 📝
- Configuration management using environment variables. 🔐
- Rate limiting to prevent abuse. 🚦
- Input sanitization for the domain parameter. 🧼
- Comprehensive unit and integration tests. 🧪

## Deployment 🚀

The application is deployed using [Fly.io](https://fly.io/). The `fly.toml` file contains the necessary configuration for the deployment.

## Monitoring 📊

The application exposes Prometheus metrics at the `/metrics` endpoint. The `domain_counter` metric tracks the number of visits to each domain.

## Running Tests 🧪

To run the tests, use the following command:

```
python -m unittest test_bounce.py
```

## Contributing 🤝

If you'd like to contribute to this project, please feel free to open an issue or submit a pull request. Let's bounce together! 🙌

Built with ❤️ by [@harperreed](https://github.com/harperreed)
