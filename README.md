
# Legal Advice API

A FastAPI-based service that provides general legal information using Large Language Models (LLMs), with comprehensive security measures and content validation.

## Disclaimer

This service provides general legal information only and does not constitute legal advice. Users should consult with qualified attorneys for specific legal matters.

## Features

- **Secure LLM Integration**: Supports both OpenAI and Ollama backends
- **Content Validation**: Advanced banned word detection with evasion prevention
- **Input Security**: Protection against prompt injection and adversarial inputs
- **Topic Filtering**: Ensures responses are limited to legal topics
- **Response Validation**: Validates LLM outputs before returning to users

## Security Features

### Input Validation
- Banned word detection with advanced evasion prevention
- Character substitution detection (k1ll, murd3r, etc.)
- Spacing evasion detection (k i l l, m-u-r-d-e-r, etc.)
- Leetspeak detection (@ss@ult, h@ck, etc.)
- Prompt injection, Red-Team detection
- Topic relevance filtering

### Response Validation
- Output scanning for banned content
- Error handling for service failures

## Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional)
- OpenAI API key  

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd MindGard-legal-advice-api
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration (especially copy your vaild OpenAI API key)
```

4. **Run the application**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Docker Deployment

**Build and run with Docker Compose**
```bash
docker-compose up --build
```

## API Usage

### Legal Advice Endpoint

**POST** `/api/v1/legal-advice`

Open http://127.0.0.1:8000/docs to test in Swagger UI.

```json
{
  "user_id": "user123",
  "input_prompt": "What are the requirements for a valid contract?"
}
```

**Response (Success)**
```json
{
  "user_id": "user123",
  "advice": "A valid contract typically requires...",
  "timestamp": "2024-01-15T10:30:00Z",
  "model_used": "gpt-4-turbo",
  "status": "success"
}
```

**Response (Validation Error)**
```json
{
  "error": "Request contains prohibited content",
  "detail": "Your request contains language that cannot be processed due to policy restrictions.",
  "banned_words_found": ["kill"],
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": "user123",
  "status": "validation_error"
}
```

### Health Check

**GET** `/health`

Returns service health status with timestamp.

## Testing

### Run All Tests
```bash
pytest -v
```

### Run Specific Test Categories
```bash
# Unit tests
pytest tests/test_validator.py -v

# API tests  
pytest tests/test_api.py -v

# Adversarial tests
pytest tests/adversarial_inputs.py -v

# LLM service tests
pytest tests/test_llm_service.py -v
```

### Test Coverage
```bash
pytest --cov=app --cov-report=html
```

## Security Considerations

### Banned Words List
The system blocks requests containing:
- Violence-related terms (kill, murder, assault, etc.)
- Criminal activities (bribe, launder, hack, etc.)
- Unauthorized legal practice terms
- System manipulation attempts (jailbreak, override, etc.)

### Advanced Evasion Prevention
- Character substitution (k1ll → kill)
- Spacing evasion (k i l l → kill)
- Leetspeak (k!ll → kill)
- Punctuation obfuscation (k.i.l.l → kill)
- Case variations (KILL, KiLl → kill)

### Response Safety
- All LLM responses are scanned for banned content
- Fallback responses for policy violations
- No specific legal advice, only general information
- Clear disclaimers about attorney-client relationships

## Monitoring and Logging

The application provides structured logging with:
- Request/response logging
- Security event logging
- Performance metrics
- Error tracking
- User activity monitoring

Logs include:
- Timestamp and service identification
- User ID and IP address (when available)
- Request validation results
- Response generation metrics
- Security violations and attempts

## Development

### Adding New Banned Words
Update `app/utils/validator.py`:
```python
BANNED_WORDS = [
    # ... existing words ...
    "new_banned_word",
]
```

### Adding New Legal Topics
Update `is_legal_topic()` in `app/utils/validator.py`:
```python
legal_keywords = [
    # ... existing keywords ...
    "new_legal_keyword",
]
```

### Testing New Security Measures
Add tests to `tests/adversarial_inputs.py`:
```python
def test_new_evasion_technique(self):
    """Test description"""
    # Test implementation
```

### Performance Optimization
- Use connection pooling for LLM APIs
- Utilize local or open-source LLMs such as Ollama
- Implement response caching for common queries
- Set up load balancing for high traffic
- Monitor and optimize token usage
- Configure appropriate timeout values
- Implement Rate Limiting
