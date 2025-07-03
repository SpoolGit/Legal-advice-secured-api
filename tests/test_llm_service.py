import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.llm_service import LLMService


class TestLLMService:
    """Test LLM service functionality"""

    @pytest.fixture
    def llm_service(self):
        return LLMService()

    @pytest.mark.asyncio
    async def test_safe_response_generation(self, llm_service):
        """Test generation of safe responses"""
        # Mock the OpenAI client that gets created in _call_openai
        with patch("openai.OpenAI") as mock_openai_class:
            # Mock the client instance
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            # Mock the response
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = (
                "This is safe legal information about contracts."
            )
            mock_response.usage = None

            # Mock the chat completions create method
            mock_client.chat.completions.create.return_value = mock_response

            # Mock the validator to return no banned words
            with patch("app.utils.validator.contains_banned_words", return_value=[]):
                result = await llm_service.generate_response(
                    "What makes a contract valid?", "test_user"
                )

                assert "contract" in result["content"]
                assert "error" not in result

    @pytest.mark.asyncio
    async def test_response_validation_failure(self, llm_service):
        """Test handling of responses with banned words"""
        # Mock the OpenAI clinet
        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            # Mock response with problematic content
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = (
                "You should kill your legal opponent."
            )
            mock_response.usage = None

            mock_client.chat.completions.create.return_value = mock_response

            # Mock validator ot detect banned words
            with patch(
                "app.utils.validator.contains_banned_words", return_value=["kill"]
            ):
                result = await llm_service.generate_response(
                    "How to win a case?", "test_user"
                )

                assert result["error"] == "response_validation_failed"
                assert "banned_words" in result
                assert "kill" in result["banned_words"]

    @pytest.mark.asyncio
    async def test_openai_api_error(self, llm_service):
        """Test handling of OpenAI API errors"""
        # Mock OpenAI client to raise exception
        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            # Make the API call raise an exception
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            result = await llm_service.generate_response("Legal question", "test_user")

            # should return error response
            assert "error" in result
            assert result["model"] == "error"
            assert "I'm sorry, I'm unable to process" in result["content"]

    @pytest.mark.asyncio
    async def test_response_validation_success(self, llm_service):
        """Test that validation passes for safe content"""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = (
                "Legal contracts require offer, acceptance, and consideration."
            )
            mock_response.usage = MagicMock()
            mock_response.usage.model_dump.return_value = {"total_tokens": 50}

            mock_client.chat.completions.create.return_value = mock_response

            # Mock validation to pass
            with patch("app.utils.validator.contains_banned_words", return_value=[]):
                result = await llm_service.generate_response(
                    "What are the elements of a contract?", "test_user"
                )

                assert "error" not in result
                assert "content" in result
                assert "contracts" in result["content"]
                assert "usage" in result
