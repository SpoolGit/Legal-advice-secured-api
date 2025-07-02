import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.models.request import LegalAdviceRequest
from app.models.response import LegalAdviceResponse, ErrorResponse, ValidationErrorResponse
from app.services.llm_service import LLMService
from app.utils.validator import validate_input_safety
from app.prompts.base_prompt import REJECTED_RISKY_INPUT_RESPONSE, OFF_TOPIC_RESPONSE

logger = logging.getLogger(__name__)
router = APIRouter()

# Dependency injection
def get_llm_service() -> LLMService:
    return LLMService()

@router.post("/legal-advice", response_model=LegalAdviceResponse)
async def get_legal_advice(
    request: LegalAdviceRequest,
    llm_service: LLMService = Depends(get_llm_service),
    http_request: Request = None
):
    """
    Generate legal advice based on user input.
    
    Args:
        request: Legal advice request containing user_id and input_prompt
        llm_service: LLM service dependency
        http_request: FastAPI request object for logging
        
    Returns:
        LegalAdviceResponse or ErrorResponse
    """
    start_time = datetime.utcnow()
    
    # Log request
    client_ip = http_request.client.host if http_request else "unknown"
    logger.info(f"Legal advice request from user {request.user_id} (IP: {client_ip})")
    
    try:
        # Validate input safety and relevance
        is_safe, banned_words_found, reason = validate_input_safety(request.input_prompt)
        
        if not is_safe:
            logger.warning(f"Request rejected for user {request.user_id}: {reason}")
            
            if banned_words_found:
                # Return validation error for banned words
                return JSONResponse(
                    status_code=403,
                    content=jsonable_encoder(ValidationErrorResponse(
                        error="Request contains prohibited contents",
                        detail=REJECTED_RISKY_INPUT_RESPONSE,
                        banned_words_found=banned_words_found,
                        timestamp=datetime.utcnow(),
                        user_id=request.user_id
                    )
                ))
            else:
                # Return error for off-topic requests
                return JSONResponse(
                    status_code=403,
                    content=jsonable_encoder(ErrorResponse(
                        error="Request outside supported scope",
                        detail=OFF_TOPIC_RESPONSE,
                        timestamp=datetime.utcnow(),
                        user_id=request.user_id
                    )
                ))
        
        # Generate response using LLM
        response_data = await llm_service.generate_response(
            request.input_prompt, 
            request.user_id
        )
        
        # Check if response generation faild
        if 'error' in response_data:
            if response_data['error'] == 'response_validation_failed':
                logger.error(f"Response validation failed for user {request.user_id}")
                return JSONResponse(
                    status_code=500,
                    content=jsonable_encoder(ValidationErrorResponse(
                        error="Response validation failed",
                        detail="Generated response contains prohibited content",
                        banned_words_found=response_data.get('banned_words', []),
                        timestamp=datetime.utcnow(),
                        user_id=request.user_id
                    ))
                )
            else:
                logger.error(f"LLM service error for user {request.user_id}: {response_data['error']}")
                return JSONResponse(
                    status_code=500,
                    content=jsonable_encoder(ValidationErrorResponse(
                        error="Service temporarily unavailable",
                        detail="Unable to process request at this time",
                        timestamp=datetime.utcnow(),
                        user_id=request.user_id
                    ))
                )
        
        # Log successful respnse
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Legal advice generated for user {request.user_id} in {processing_time:.2f}s")
        
        return LegalAdviceResponse(
            user_id=request.user_id,
            advice=response_data['content'],
            timestamp=datetime.utcnow(),
            model_used=response_data['model']
        )
        
    except Exception as e:
        logger.error(f"Unexpceted error for user {request.user_id}: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal server error",
                detail="An unexpected error occurred",
                timestamp=datetime.utcnow(),
                user_id=request.user_id
            ).dict()
        )

@router.get("/health")
async def health_check():
    """Health check endpoint for the legal advice service"""
    return {
        "status": "healthy",
        "service": "legal-advice-api",
        "timestamp": datetime.utcnow().isoformat()
    }