import logging
import sys
from datetime import datetime
from app.config import settings

class CustomFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record):
        # Add timestamp
        record.timestamp = datetime.utcnow().isoformat()
        
        # Add service name
        record.service = "legal-advice-api"
        
        return super().format(record)

def setup_logging():
    """Setup application logging"""
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Create formatter
    formatter = CustomFormatter(
        fmt='%(timestamp)s - %(service)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)