# syntax=docker/dockerfile:1.9
# Start with Ubuntu noble as the base image and name this stage 'build'
FROM ubuntu:noble AS build

# Set shell to sh with explicit command echoing and exit on error
SHELL ["sh", "-exc"]

# Copy the uv executable from the specified image to local bin directory
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy all files from the build context to the container
COPY . .

# Expose port 8080 for the application
EXPOSE 8080

# Run the application using uv to execute gunicorn with the bounce:app WSGI application
CMD ["uv","run", "gunicorn","bounce:app"]
