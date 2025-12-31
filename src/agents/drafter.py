import json
from typing import Dict, Any, List
from src.core.workflow_state import WorkflowState
from src.agents.base_agent import BaseAgent
from src.services.llm_gateway import LLMGateway
from src.Utils.prompt_loader import load_prompts

class DraftingAgent(BaseAgent):
    """
    Specialist: Assembles final JSON pages using Templates.
    """
    def __init__(self, llm_gateway: LLMGateway = None):
        super().__init__(agent_name="Drafter")
        self.llm_gateway = llm_gateway or LLMGateway()
        self.prompts = load_prompts().get("content_factory", {})

    def process(self, state: WorkflowState) -> WorkflowState:
        print(f"[{self.agent_name}] Drafting content pages...")

        if not state.product_page:
            state.product_page = self._build_product_page(state.product_data)
        
        if not state.faq_page:
            state.faq_page = self._build_faq_page(state.product_data, state.generated_questions)

        if not state.comparison_page:
            state.comparison_page = self._build_comparison_page(state.product_data, state.competitor_data)
            
        return state

    def _build_product_page(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Simple Template Assembly
        return {
            "page_type": "product_listing",
            "title": data.get("product_name"),
            "price": data.get("price"),
            "content": "Generated via Agent System" # Simplified for brevity
        }

    def _build_faq_page(self, data: Dict[str, Any], questions: List[str]) -> Dict[str, Any]:
        # In a real run, you'd call LLM here to answer questions
        return {
            "page_type": "faq",
            "questions": questions[:5]
        }

    def _build_comparison_page(self, us: Dict[str, Any], them: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "page_type": "comparison",
            "us": us.get("product_name"),
            "them": them.get("product_name")
        }