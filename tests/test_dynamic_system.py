import pytest
import json
from unittest.mock import MagicMock

from src.core.workflow_state import WorkflowState
from src.core.orchestrator import Orchestrator
from src.agents.supervisor import SupervisorAgent
from src.agents.reviewer import ReviewerAgent

# --- MOCKS ---

class MockLLMGateway:
    """Simulates LLM responses for the Supervisor."""
    def __init__(self, responses=None):
        self.responses = responses or []
        self.call_count = 0

    def chat_completion(self, messages, temperature=0.0, response_format="json_object"):
        # Just return the next mock response
        if self.call_count < len(self.responses):
            resp = self.responses[self.call_count]
            self.call_count += 1
            return resp
        return "{}"

# --- UNIT TESTS: SUPERVISOR LOGIC ---

def test_supervisor_routes_to_ingestor_when_empty():
    """Scenario: System is fresh. Supervisor should pick 'ingestor'."""
    agent = SupervisorAgent(llm_gateway=MockLLMGateway())
    state = WorkflowState(raw_input="Some text")
    
    # Pre-condition: No product data
    assert state.product_data == {}
    
    new_state = agent.process(state)
    
    assert new_state.next_agent == "ingestor"

def test_supervisor_routes_to_researcher_when_data_exists():
    """Scenario: We have data, but no research. Go to 'researcher'."""
    agent = SupervisorAgent(llm_gateway=MockLLMGateway())
    state = WorkflowState(
        product_data={"product_name": "Test", "price": "$10"},
        raw_input="done"
    )
    
    new_state = agent.process(state)
    
    assert new_state.next_agent == "researcher"

def test_supervisor_routes_to_drafter_when_research_done():
    """Scenario: Research complete. Go to 'drafter'."""
    agent = SupervisorAgent(llm_gateway=MockLLMGateway())
    state = WorkflowState(
        product_data={"product_name": "Test", "price": "$10"},
        competitor_data={"name": "Comp"},
        generated_questions=["Q1"],
        # Missing pages -> Draft
        product_page=None 
    )
    
    new_state = agent.process(state)
    
    assert new_state.next_agent == "drafter"

def test_supervisor_routes_to_reviewer_after_drafting():
    """Scenario: Pages just created. Must go to 'reviewer'."""
    agent = SupervisorAgent(llm_gateway=MockLLMGateway())
    state = WorkflowState(
        product_data={"name": "Test"},
        competitor_data={"name": "Comp"},
        generated_questions=["Q1"],
        # Pages exist
        product_page={"content": "stuff"},
        faq_page={"questions": []},
        comparison_page={"table": []},
        # Metadata check
        last_agent="drafter" 
    )
    
    new_state = agent.process(state)
    
    assert new_state.next_agent == "reviewer"

# --- UNIT TESTS: REVIEWER FEEDBACK LOOP ---

def test_reviewer_rejects_bad_content():
    """Scenario: Drafter produced empty pages. Reviewer should fail it."""
    agent = ReviewerAgent()
    state = WorkflowState(
        product_page={} # Empty page (Bad!)
    )
    
    new_state = agent.process(state)
    
    # Expect failure
    assert len(new_state.errors) > 0
    assert "ReviewFeedback" in new_state.errors[0]
    # Expect reset (Self-Correction Trigger)
    assert new_state.product_page is None

def test_reviewer_passes_good_content():
    """Scenario: Content is solid. Reviewer adds no errors."""
    agent = ReviewerAgent()
    state = WorkflowState(
        product_page={"content": "Good stuff"},
        faq_page={"questions": ["Q1", "Q2", "Q3"]},
        comparison_page={"table": ["data"]}
    )
    
    new_state = agent.process(state)
    
    assert new_state.errors == []

# --- INTEGRATION TEST: CIRCUIT BREAKER ---

def test_supervisor_stops_on_critical_error():
    """Scenario: An agent crashed. Supervisor should STOP, not loop."""
    agent = SupervisorAgent()
    state = WorkflowState()
    state.add_error("CRITICAL: API Failed")
    
    new_state = agent.process(state)
    
    assert new_state.is_complete is True
    assert new_state.next_agent == "FINISH"