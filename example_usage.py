# ABOUTME: Example usage of the domain submission API
# ABOUTME: Shows how to run the server and make requests to the /submit endpoint

import os
import requests
import uvicorn
from submit import app

# Example environment variables you'll need to set:
# export RECAPTCHA_SECRET_KEY="your_recaptcha_secret_key"
# export AIRTABLE_API_KEY="your_airtable_api_key"
# export AIRTABLE_BASE_ID="your_airtable_base_id"
# export AIRTABLE_TABLE_ID="your_airtable_table_id"

def run_server():
    """Run the FastAPI server."""
    print("Starting domain submission API server...")
    print("API will be available at: http://localhost:8000")
    print("OpenAPI docs at: http://localhost:8000/docs")
    print("Health check at: http://localhost:8000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

def example_request():
    """Example of making a request to the /submit endpoint."""
    url = "http://localhost:8000/submit"
    
    # Example form data
    form_data = {
        "email": "example@domain.com",
        "name": "John Doe",
        "domain_name": "example.com",
        "budget": 10000,
        "note": "Looking for a premium domain for my startup"
    }
    
    # Example reCAPTCHA token (you'd get this from the frontend)
    recaptcha_token = "your_recaptcha_token_here"
    
    try:
        response = requests.post(
            url,
            json=form_data,
            params={"recaptcha_token": recaptcha_token},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("duplicate"):
                print("✓ Submission already exists")
            else:
                print("✓ New submission created and synced to Airtable")
        else:
            print(f"✗ Error: {response.json().get('error', 'Unknown error')}")
            
    except requests.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Run the server
    run_server()
    
    # To test with example request, uncomment:
    # example_request()