import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)

class TestLegalAdviceAPI:
    """Test the legal advice API endpoints"""
    
    def test_valid_legal_request(self):
        """Test valid legal advice request"""
        with patch('app.services.llm_service.LLMService.generate_response') as mock_llm:
            mock_llm.return_value = {
                'content': 'This is general legal information about contracts.',
                'model': 'gpt-3.5-turbo'
            }
            
            response = client.post("/api/v1/legal-advice", json={
                "user_id": "test_user_123",
                "input_prompt": "What makes a contract legally binding?"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["user_id"] == "test_user_123"
            assert "advice" in data
    
    def test_banned_words_rejection(self):
        """Test rejection of requests with banned words"""
        response = client.post("/api/v1/legal-advice", json={
            "user_id": "test_user_123",
            "input_prompt": "How can I kill my business partner legally?"
        })
        
        assert response.status_code == 403
        data = response.json()
        assert data["status"] == "validation_error"
        assert "banned_words_found" in data
        assert "kill" in data["banned_words_found"]
    
    def test_off_topic_rejection(self):
        """Test rejection of off-topic requests"""
        response = client.post("/api/v1/legal-advice", json={
            "user_id": "test_user_123",
            "input_prompt": "How do I cook pasta?"
        })
        
        assert response.status_code == 403
        data = response.json()
        assert data["status"] == "error"
        assert "outside the supported scope" in data["detail"]
    
    def test_invalid_user_id(self):
        """Test rejection of invalid user ID"""
        response = client.post("/api/v1/legal-advice", json={
            "user_id": "invalid@user!",
            "input_prompt": "What are my rights?"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_empty_input_prompt(self):
        """Test rejection of empty input prompt"""
        response = client.post("/api/v1/legal-advice", json={
            "user_id": "test_user_123",
            "input_prompt": ""
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_input_too_long(self):
        """Test rejection of input that's too long"""
        long_input = "a" * 20001  # Exceeds max length
        
        response = client.post("/api/v1/legal-advice", json={
            "user_id": "test_user_123",
            "input_prompt": long_input
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_llm_service_error_handling(self):
        """Test handling of LLM service errors"""
        with patch('app.services.llm_service.LLMService.generate_response') as mock_llm:
            mock_llm.return_value = {
                'content': 'Error response',
                'model': 'error',
                'error': 'Service unavailable'
            }
            
            response = client.post("/api/v1/legal-advice", json={
                "user_id": "test_user_123",
                "input_prompt": "What are employment laws?"
            })
            
            assert response.status_code == 500
            data = response.json()
            assert data["status"] == "validation_error"