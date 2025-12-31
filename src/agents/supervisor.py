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
        # 0. CIRCUIT BREAKER
        # If we looped too many times, just stop.
        if state.errors and "ReviewFeedback" not in state.errors[-1]: 
             # Only stop for critical errors, not feedback loops
             state.next_agent = "FINISH"
             state.is_complete = True
             return state

        # 1. Completion Check
        # If all pages exist AND we haven't just come from the Drafter, run Reviewer
        if state.product_page and state.faq_page and state.comparison_page:
            if state.last_agent == "drafter":
                state.next_agent = "reviewer"
                return state
            
            # If we came from Reviewer and pages still exist, it means we passed!
            if state.last_agent == "reviewer":
                state.next_agent = "FINISH"
                state.is_complete = True
                return state

        # 2. Dynamic Routing Logic
        if not state.product_data:
            state.next_agent = "ingestor"
            return state

        if not state.competitor_data or not state.generated_questions:
            state.next_agent = "researcher"
            return state

        if not state.product_page or not state.faq_page or not state.comparison_page:
            state.next_agent = "drafter"
            return state

        state.next_agent = "FINISH"
        state.is_complete = True
        return state