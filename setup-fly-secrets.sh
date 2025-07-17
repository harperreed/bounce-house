#!/bin/bash

# ABOUTME: Script to set up Fly.io secrets for the Bounce House application
# ABOUTME: Prompts for required environment variables and sets them as Fly.io secrets

set -e

echo "🚀 Setting up Fly.io secrets for Bounce House"
echo "=============================================="

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl is not installed. Please install it first:"
    echo "   curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Check if logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "❌ You're not logged in to Fly.io. Please run: flyctl auth login"
    exit 1
fi

# Get app name (default to bounce-house)
read -p "Enter your Fly.io app name (default: bounce-house): " APP_NAME
APP_NAME=${APP_NAME:-bounce-house}

echo ""
echo "📝 Please provide the following required secrets:"
echo ""

# Get reCAPTCHA secret key
read -p "Enter your reCAPTCHA secret key: " RECAPTCHA_SECRET_KEY
if [ -z "$RECAPTCHA_SECRET_KEY" ]; then
    echo "❌ reCAPTCHA secret key is required"
    exit 1
fi

# Get Airtable API key
read -p "Enter your Airtable API key: " AIRTABLE_API_KEY
if [ -z "$AIRTABLE_API_KEY" ]; then
    echo "❌ Airtable API key is required"
    exit 1
fi

# Get Airtable base ID
read -p "Enter your Airtable base ID: " AIRTABLE_BASE_ID
if [ -z "$AIRTABLE_BASE_ID" ]; then
    echo "❌ Airtable base ID is required"
    exit 1
fi

# Get Airtable table ID
read -p "Enter your Airtable table ID: " AIRTABLE_TABLE_ID
if [ -z "$AIRTABLE_TABLE_ID" ]; then
    echo "❌ Airtable table ID is required"
    exit 1
fi

# Optional: Get allowed origins for CORS
read -p "Enter allowed origins for CORS (comma-separated, optional): " ALLOWED_ORIGINS

echo ""
echo "🔒 Setting secrets for app: $APP_NAME"
echo ""

# Set required secrets
flyctl secrets set RECAPTCHA_SECRET_KEY="$RECAPTCHA_SECRET_KEY" --app "$APP_NAME"
flyctl secrets set AIRTABLE_API_KEY="$AIRTABLE_API_KEY" --app "$APP_NAME"
flyctl secrets set AIRTABLE_BASE_ID="$AIRTABLE_BASE_ID" --app "$APP_NAME"
flyctl secrets set AIRTABLE_TABLE_ID="$AIRTABLE_TABLE_ID" --app "$APP_NAME"

# Set optional CORS origins
if [ -n "$ALLOWED_ORIGINS" ]; then
    flyctl secrets set ALLOWED_ORIGINS="$ALLOWED_ORIGINS" --app "$APP_NAME"
fi

echo ""
echo "✅ Secrets have been set successfully!"
echo ""
echo "🔍 You can verify the secrets with:"
echo "   flyctl secrets list --app $APP_NAME"
echo ""
echo "🚀 You're ready to deploy! Push to main branch or create a PR to trigger deployment."