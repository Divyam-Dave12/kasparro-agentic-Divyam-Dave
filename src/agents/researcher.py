import json
from typing import Dict, Any, List
from src.core.workflow_state import WorkflowState
from src.agents.base_agent import BaseAgent
from src.services.llm_gateway import LLMGateway
from src.Utils.prompt_loader import load_prompts

class ResearchAgent(BaseAgent):
    """
    Specialist: Generates auxiliary data (Competitor, Questions).
    """
    def __init__(self, llm_gateway: LLMGateway = None):
        super().__init__(agent_name="Researcher")
        self.llm_gateway = llm_gateway or LLMGateway()
        self.prompts = load_prompts().get("content_factory", {}) # Reusing existing prompts

    def process(self, state: WorkflowState) -> WorkflowState:
        print(f"[{self.agent_name}] Conducting research...")

        # 1. Generate Competitor
        if not state.competitor_data:
            state.competitor_data = self._generate_competitor()

        # 2. Generate Questions
        if not state.generated_questions:
            state.generated_questions = self._generate_questions(state.product_data)
            
        return state

    def _generate_competitor(self) -> Dict[str, Any]:
        prompt = self.prompts.get("competitor_prompt", "Generate competitor JSON")
        return self._call_llm_json(prompt)

    def _generate_questions(self, product_data: Dict[str, Any]) -> List[str]:
        raw_prompt = self.prompts.get("questions_prompt", "Generate questions JSON")
        prompt = raw_prompt.replace("{data_str}", json.dumps(product_data))
        response = self._call_llm_json(prompt)
        return response.get("questions", [])

    def _call_llm_json(self, prompt: str) -> Dict[str, Any]:
        try:
            messages = [{"role": "user", "content": prompt}]
            resp = self.llm_gateway.chat_completion(messages, response_format="json_object")
            return json.loads(resp)
        except Exception as e:
            print(f"Research Error: {e}")
            return {}