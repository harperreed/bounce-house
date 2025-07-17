# ABOUTME: Airtable client for syncing domain submissions to external database
# ABOUTME: Handles creating records in Airtable with retry logic and error handling

import requests
import os
import time
from typing import Optional
from models import FormInput


class AirtableClient:
    def __init__(
        self, 
        api_key: Optional[str] = None,
        base_id: Optional[str] = None,
        table_id: Optional[str] = None
    ):
        self.api_key = api_key or os.environ.get("AIRTABLE_API_KEY")
        self.base_id = base_id or os.environ.get("AIRTABLE_BASE_ID")
        self.table_id = table_id or os.environ.get("AIRTABLE_TABLE_ID")
        
        if not all([self.api_key, self.base_id, self.table_id]):
            raise ValueError("Missing Airtable configuration (AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID)")
        
    def create_record(self, form_data: FormInput) -> str:
        """Create a record in Airtable and return the record ID."""
        url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_id}"
        
        fields = {
            "email": form_data.email,
            "name": form_data.name,
            "domain_name": form_data.domain_name
        }
        
        if form_data.budget is not None:
            fields["budget_cents"] = form_data.budget
            
        if form_data.note:
            fields["note"] = form_data.note
            
        data = {
            "records": [{
                "fields": fields
            }]
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=data, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                if not result.get("records"):
                    raise ValueError("No record returned from Airtable")
                    
                return result["records"][0]["id"]
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise ValueError(f"Airtable API request failed after {max_retries} attempts: {str(e)}")
                    
                # Exponential backoff: 1s, 2s, 4s
                time.sleep(2 ** attempt)
                
        raise ValueError("Airtable sync failed after all retries")