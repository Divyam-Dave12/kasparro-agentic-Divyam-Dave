import json
import re
from typing import Optional, Dict, Any

from src.core.workflow_state import WorkflowState
from src.agents.base_agent import BaseAgent
from src.schemas.product_data import ProductData
from src.services.llm_gateway import LLMGateway
from src.Utils.prompt_loader import load_prompts

class DataIngestionAgent(BaseAgent):
    """
    Data Ingestion Agent (JSON-Strict).
    """

    def __init__(self, llm_gateway: Optional[LLMGateway] = None):
        super().__init__(agent_name="Data Ingestion")
        self.llm_gateway = llm_gateway or LLMGateway()
        
        # Safe load prompts
        try:
            self.prompts = load_prompts()
        except Exception:
            self.prompts = {}

    def process(self, state: WorkflowState) -> WorkflowState:
        # PATH A: Structured Data Exists
        if state.product_data:
            return self._validate_and_update(state, state.product_data)

        # PATH B: Raw Text -> Extract JSON
        if state.raw_input:
            # We pass 'state' so we can log errors if extraction crashes
            extracted_json = self._extract_json_from_text(state, state.raw_input)
            
            if extracted_json:
                return self._validate_and_update(state, extracted_json)
            
            # If extraction failed but didn't log a specific error yet
            if not state.errors:
                state.add_error("DataIngestion: Extraction returned empty data.")
            return state
        
        state.add_error("DataIngestion: No valid input provided.")
        return state

    def _extract_json_from_text(self, state: WorkflowState, raw_text: str) -> Dict[str, Any]:
        """
        Uses LLM to transform text into a Dict.
        """
        # 1. Get Prompt from YAML
        system_prompt = self.prompts.get("data_ingestion", {}).get("extraction_prompt", "")
        if not system_prompt:
             # Fallback if YAML is broken
             system_prompt = "You are a data extractor. Return JSON."

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": raw_text}
            ]
            
            # 2. Call LLM
            response_str = self.llm_gateway.chat_completion(
                messages=messages,
                temperature=0.0, 
                response_format="json_object"
            )
            
            # 3. Parse Response
            cleaned_str = self._sanitize_json(response_str)
            return json.loads(cleaned_str)
            
        except Exception as e:
            # 4. Log Crash to State
            error_msg = f"DataIngestion: JSON Extraction Crashed. Error: {str(e)}"
            print(error_msg)
            state.add_error(error_msg)
            return {}

    def _validate_and_update(self, state: WorkflowState, data: Dict[str, Any]) -> WorkflowState:
        """Validates the Dict and saves it to State."""
        try:
            # Pydantic validates the structure
            validated_model = ProductData(**data)
            
            # Save as Dict
            state.product_data = validated_model.model_dump()
            
        except Exception as e:
            state.add_error(f"DataIngestion: Schema Validation Failed. {str(e)}")
            
        return state

    def _sanitize_json(self, json_str: str) -> str:
        if not json_str: return "{}"
        pattern = r"```(?:json)?\s*(.*?)```"
        match = re.search(pattern, json_str, re.DOTALL)
        if match: return match.group(1).strip()
        return json_str.strip()