# ABOUTME: Pydantic models for form validation and data structures
# ABOUTME: Defines the FormInput model with validation rules for domain submissions

from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from typing import Optional


class FormInput(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    budget: Optional[int] = Field(None, ge=0, le=1000000)
    domain_name: str
    note: Optional[str] = Field(None, max_length=1000)
    hp_field: Optional[str] = None  # honeypot field
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', v):
            raise ValueError('Name contains invalid characters')
        return v
        
    @field_validator('domain_name')
    @classmethod
    def validate_domain(cls, v):
        if not v or '.' not in v:
            raise ValueError('Invalid domain format')
        if not re.match(r'^[a-zA-Z0-9.-]+$', v):
            raise ValueError('Invalid domain characters')
        if len(v) > 253:
            raise ValueError('Domain too long')
        return v


class SubmissionRequest(BaseModel):
    form_data: FormInput
    recaptcha_token: str