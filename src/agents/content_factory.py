import json
import re
from typing import Dict, Any, List, Optional

from src.core.workflow_state import WorkflowState
from src.agents.base_agent import BaseAgent
from src.services.llm_gateway import LLMGateway
from src.Utils.prompt_loader import load_prompts

class ContentFactoryAgent(BaseAgent):
    """
    Content Factory Agent (JSON-Strict).
    
    pipeline:
    JSON Input (Product Data) -> Logic Blocks -> JSON Output (Pages)
    """

    def __init__(self, llm_gateway: Optional[LLMGateway] = None):
        super().__init__(agent_name="Content Factory")
        self.llm_gateway = llm_gateway or LLMGateway()
        self.prompts = load_prompts().get("content_factory", {})

    def _generate_questions_json(self, product_data: Dict[str, Any]) -> List[str]:
        data_str = json.dumps(product_data)
        
        # USE YAML TEMPLATE
        raw_template = self.prompts.get("questions_prompt", "")
        
        # Fill in the dynamic parts (f-string replacement happens here manually)
        prompt = raw_template.replace("{data_str}", data_str)
        
        response = self._call_llm_json(prompt)
        return response.get("questions", [])

    def process(self, state: WorkflowState) -> WorkflowState:
        if not state.product_data:
            state.add_error("ContentFactory: Missing 'product_data' JSON.")
            return state

        # 1. Generate Competitor JSON
        if not state.competitor_data:
            state.competitor_data = self._generate_competitor_json()

        # 2. Generate Questions JSON
        if not state.generated_questions:
            state.generated_questions = self._generate_questions_json(state.product_data)

        # 3. Assemble Final JSON Artifacts
        state.product_page = self._build_product_page(state.product_data)
        state.faq_page = self._build_faq_page(state.product_data, state.generated_questions)
        state.comparison_page = self._build_comparison_page(state.product_data, state.competitor_data)

        print(f"[{self.agent_name}] All JSON artifacts generated successfully.")
        return state

    # --- JSON GENERATORS ---

    def _generate_competitor_json(self) -> Dict[str, Any]:
        prompt = (
            "Create a fictional competitor product.\n"
            "Return JSON: { 'product_name': str, 'price': str, 'key_ingredients': [str], 'benefits': [str] }"
        )
        return self._call_llm_json(prompt)

    def _generate_questions_json(self, product_data: Dict[str, Any]) -> List[str]:
        data_str = json.dumps(product_data)
        prompt = (
            f"Data: {data_str}\n"
            "Generate 15 categorized user questions.\n"
            "Return JSON: { 'questions': ['Q1', 'Q2', ...] }"
        )
        response = self._call_llm_json(prompt)
        return response.get("questions", [])

    # --- JSON PAGE ASSEMBLERS ---

    def _build_product_page(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Generate description using LLM
        desc_prompt = f"Write a description for {data.get('product_name')}. Return JSON: {{'description': '...'}}"
        desc_json = self._call_llm_json(desc_prompt)
        
        # Assemble JSON strictly
        return {
            "page_type": "product_listing",
            "meta": {
                "title": data.get("product_name"),
                "price": data.get("price")
            },
            "content": {
                "headline": f"Discover {data.get('product_name')}",
                "description": desc_json.get("description", ""),
                "specs": {
                    "ingredients": data.get("key_ingredients", []),
                    "usage": data.get("how_to_use", "")
                }
            }
        }

    def _build_faq_page(self, data: Dict[str, Any], questions: List[str]) -> Dict[str, Any]:
        # We process top 5 questions for efficiency
        subset = questions[:5] if questions else ["How do I use this?"]
        
        prompt = (
            f"Product: {json.dumps(data)}\n"
            f"Questions: {json.dumps(subset)}\n"
            "Answer strictly based on facts.\n"
            "Return JSON: { 'faqs': [{'question': '...', 'answer': '...'}] }"
        )
        response = self._call_llm_json(prompt)
        
        return {
            "page_type": "faq",
            "data": response.get("faqs", [])
        }

    def _build_comparison_page(self, us: Dict[str, Any], them: Dict[str, Any]) -> Dict[str, Any]:
        # Pure Logic (No LLM needed for simple table assembly)
        return {
            "page_type": "comparison",
            "title": f"{us.get('product_name')} vs {them.get('product_name')}",
            "table": [
                {"feature": "Price", "us": us.get("price"), "them": them.get("price")},
                {"feature": "Ingredients", "us": us.get("key_ingredients"), "them": them.get("key_ingredients")}
            ]
        }

    # --- HELPER ---
    def _call_llm_json(self, prompt: str) -> Dict[str, Any]:
        """Ensures input and output are handled as strictly JSON."""
        try:
            messages = [{"role": "system", "content": "Return ONLY valid JSON."}, {"role": "user", "content": prompt}]
            raw = self.llm_gateway.chat_completion(messages=messages, temperature=0.3, response_format="json_object")
            return json.loads(self._sanitize_json(raw))
        except Exception as e:
            print(f"[{self.agent_name}] LLM JSON Error: {e}")
            return {}

    def _sanitize_json(self, json_str: str) -> str:
        if not json_str: return "{}"
        pattern = r"```(?:json)?\s*(.*?)```"
        match = re.search(pattern, json_str, re.DOTALL)
        if match: return match.group(1).strip()
        return json_str.strip()