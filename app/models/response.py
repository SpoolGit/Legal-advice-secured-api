from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LegalAdviceResponse(BaseModel):
    user_id: str
    advice: str
    timestamp: datetime
    model_used: str
    status: str = "success"

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime
    user_id: Optional[str] = None
    status: str = "error"
    
class ValidationErrorResponse(BaseModel):
    error: str
    detail: str
    banned_words_found: Optional[List[str]] = None
    timestamp: datetime
    user_id: Optional[str] = None
    status: str = "validation_error"