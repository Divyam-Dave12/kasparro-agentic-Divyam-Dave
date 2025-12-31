from src.core.workflow_state import WorkflowState
from src.agents.base_agent import BaseAgent

class ReviewerAgent(BaseAgent):
    """
    Quality Assurance Agent.
    Checks if the generated pages are populated and high quality.
    """
    def __init__(self):
        super().__init__(agent_name="Reviewer")

    def process(self, state: WorkflowState) -> WorkflowState:
        print(f"[{self.agent_name}] conducting quality check...")
        
        errors = []
        
        # Check Product Page
        if not state.product_page or "content" not in state.product_page:
            errors.append("Product page is missing content.")
            
        # Check FAQ
        if not state.faq_page or len(state.faq_page.get("questions", [])) < 3:
            errors.append("FAQ page has too few questions.")

        # Check Comparison
        if not state.comparison_page:
            errors.append("Comparison page is missing.")

        if errors:
            print(f"[{self.agent_name}] ❌ Quality Check Failed: {errors}")
            # IMPORTANT: We add the errors to a specific 'feedback' field
            # so the Drafter knows what to fix.
            state.add_error(f"ReviewFeedback: {'; '.join(errors)}")
            # We clear the pages so the system knows to regenerate them
            state.product_page = None 
            state.faq_page = None
            # The Supervisor will see these are missing and re-trigger the Drafter
        else:
            print(f"[{self.agent_name}] ✅ Quality Check Passed!")
            
        return state