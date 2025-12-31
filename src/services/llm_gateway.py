import os
import google.generativeai as genai
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class LLMGateway:
    """
    Gemini Gateway (Auto-Discovery Mode).
    Automatically finds a valid model to avoid 404 errors.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing Gemini API Key in .env")

        genai.configure(api_key=api_key)
        
        # AUTO-DISCOVERY LOGIC
        self.model_name = self._find_working_model()
        print(f"✅ Gemini Gateway initialized using: {self.model_name}")

    def _find_working_model(self) -> str:
        """Query the API to find the first available text generation model."""
        try:
            # List all models the key has access to
            for m in genai.list_models():
                # We need a model that supports 'generateContent' and is a 'gemini' model
                if 'generateContent' in m.supported_generation_methods:
                    if 'gemini' in m.name.lower() and 'vision' not in m.name.lower():
                        return m.name
            
            # Fallback if list_models fails or returns nothing useful
            return "models/gemini-pro"
        except Exception as e:
            print(f"⚠️ Model Discovery Failed: {e}")
            return "models/gemini-pro"

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        response_format: str = "text",
    ) -> Optional[str]:
        
        try:
            # Adapt Prompts
            system_prompt = None
            user_prompt = ""
            for msg in messages:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                elif msg["role"] == "user":
                    user_prompt += msg["content"] + "\n"

            # Configure
            generation_config = {"temperature": temperature}
            if response_format == "json_object":
                generation_config["response_mime_type"] = "application/json"

            # Init Model with the auto-detected name
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt,
                generation_config=generation_config
            )

            response = model.generate_content(user_prompt)
            return response.text if response.text else "{}"

        except Exception as e:
            print(f"❌ Gemini Error ({self.model_name}): {str(e)}")
            return "{}"