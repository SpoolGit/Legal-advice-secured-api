import logging
import asyncio
from typing import Optional, Dict, Any
import openai
import httpx
from app.config import settings
from app.prompts.base_prompt import SYSTEM_PROMPT, get_user_prompt
from app.utils.validator import contains_banned_words

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with OpenAI"""

    def __init__(self):
        self.openai_available = bool(settings.OPENAI_API_KEY)
        if self.openai_available:
            openai.api_key = settings.OPENAI_API_KEY

    async def generate_response(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """
        Generate response from LLM with safety checks.

        Args:
            user_input: User's legal question
            user_id: User identifier for logging

        Returns:
            Dictionary containing response and metadata
        """
        try:
            # Prepare the prompt
            user_prompt = get_user_prompt(user_input)

            response = await self._call_openai(user_prompt, user_id)

            # Validate response for banned words
            banned_words_in_response = contains_banned_words(response["content"])
            if banned_words_in_response:
                logger.error(
                    f"Generated response contains banned words: {banned_words_in_response}"
                )
                return {
                    "content": "I'm sorry, I cannot provide a response to that request.",
                    "model": response["model"],
                    "error": "response_validation_failed",
                    "banned_words": banned_words_in_response,
                }

            return response

        except Exception as e:
            logger.error(f"Error generating response for user {user_id}: {e}")
            return {
                "content": "I'm sorry, I'm unable to process your request at this time.",
                "model": "error",
                "error": str(e),
            }

    async def _call_openai(self, prompt: str, user_id: str) -> Dict[str, Any]:
        """Call OpenAI API using new SDK"""

        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE,
                user=user_id,  # For usage tracking
            )

            content = response.choices[0].message.content.strip()

            logger.info(f"OpenAI response generated for user {user_id}")

            return {
                "content": content,
                "model": settings.OPENAI_MODEL,
                "usage": response.usage.model_dump() if response.usage else None,
            }

        except Exception as e:
            logger.error(f"OpenAI API error for user {user_id}: {e}")
            raise
