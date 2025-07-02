from pydantic import BaseModel, Field, validator
from typing import Optional
from app.config import settings
import re

class LegalAdviceRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100, description="Unique identifier for the user")
    input_prompt: str = Field(..., min_length=1, description="Legal question from user")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        # Basic sanitization - alphanumeric and common separators only
        # This needs to be repalces with actual user validation using Auth0 or similar service
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('user_id must contain only alphanumeric characters, hyphens, and underscores')
        return v
    
    @validator('input_prompt')
    def validate_input_prompt(cls, v):
        # Basic input sanitization
        v = v.strip()
        if not v:
            raise ValueError('input_prompt cannot be empty')
            
        if len(v) > settings.MAX_INPUT_LENGTH:
            raise ValueError(f"input_prompt exceeds maximum allowed length of {settings.MAX_INPUT_LENGTH}")
            
        # Check for potential injection attempts
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'data:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
            r'<iframe',
            r'<object',
            r'<embed'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('input_prompt contains potentially unsafe content')
        
        return v