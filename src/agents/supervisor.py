from src.core.workflow_state import WorkflowState
from src.agents.base_agent import BaseAgent
from src.services.llm_gateway import LLMGateway

class SupervisorAgent(BaseAgent):
    """
    The Brain. Decides the next step based on data availability.
    """
    def __init__(self, llm_gateway: LLMGateway = None):
        super().__init__(agent_name="Supervisor")
        self.llm_gateway = llm_gateway or LLMGateway()

    def process(self, state: WorkflowState) -> WorkflowState:
        # 0. CIRCUIT BREAKER: If errors exist, STOP immediately.
        if state.errors:
            print(f"[{self.agent_name}] 🛑 Errors detected. Stopping workflow.")
            state.next_agent = "FINISH"
            state.is_complete = True
            return state

        # 1. Check if we are done (All 3 pages exist)
        if state.faq_page and state.product_page and state.comparison_page:
            state.next_agent = "FINISH"
            state.is_complete = True
            return state

        # 2. Dynamic Routing Logic
        
        # Priority 1: No data? -> Ingest
        if not state.product_data:
            state.next_agent = "ingestor"
            return state

        # Priority 2: Data exists, but missing research? -> Research
        if not state.competitor_data or not state.generated_questions:
            state.next_agent = "researcher"
            return state

        # Priority 3: Research done, but missing pages? -> Draft
        if not state.faq_page or not state.product_page or not state.comparison_page:
            state.next_agent = "drafter"
            return state

        # Fallback
        state.next_agent = "FINISH"
        state.is_complete = True
        return state