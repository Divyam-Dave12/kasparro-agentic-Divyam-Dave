import time
from typing import List, Dict, Optional

from openai import OpenAI, OpenAIError

from config.settings import settings


class LLMGateway:
    """
    LLM Gateway.

    Responsibilities:
    - Abstract interaction with the LLM provider
    - Centralize model and API configuration
    - Provide a stable interface for agent usage
    - Handle transient failures with minimal retry logic
    """

    def __init__(self):
        """
        Initialize the LLM client using centralized settings.
        """
        if not settings.OPENAI_API_KEY:
            raise ValueError("LLMGateway: OPENAI_API_KEY is not configured.")

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        response_format: str = "text",
    ) -> Optional[str]:
        """
        Executes a chat completion request.

        Args:
            messages: OpenAI-style message list
            temperature: Creativity control
            response_format: 'text' or 'json_object'

        Returns:
            Raw string response from the LLM, or None if failure occurs.
        """
        api_response_format = (
            {"type": "json_object"}
            if response_format == "json_object"
            else {"type": "text"}
        )

        max_retries = 1
        last_error: Optional[Exception] = None

        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    response_format=api_response_format,
                )

                return response.choices[0].message.content

            except OpenAIError as e:
                last_error = e
                if attempt < max_retries:
                    time.sleep(1)
                else:
                    return None

            except Exception as e:
                return None

        return None
