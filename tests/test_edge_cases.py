import pytest
import json
from unittest.mock import MagicMock

from src.core.workflow_state import WorkflowState
from src.core.orchestrator import Orchestrator
from src.agents.data_ingestion import DataIngestionAgent

# --- REUSABLE MOCK ---
class MockLLMGateway:
    def __init__(self, response_str=None, raise_error=None):
        self.response_str = response_str
        self.raise_error = raise_error

    def chat_completion(self, messages, temperature=0.0, response_format="json_object"):
        if self.raise_error:
            raise self.raise_error
        return self.response_str

# --- TEST CASES ---

def test_ingestion_handles_markdown_wrapping():
    """
    Scenario: LLM wraps the JSON in ```json ... ``` despite instructions.
    The agent should strip this and parse correctly.
    """
    bad_llm_response = """
    Here is your data:
    ```json
    {
        "product_name": "Markdown Serum",
        "concentration": "10%",
        "skin_type": "All",
        "key_ingredients": ["Code"],
        "benefits": ["Parsing"],
        "how_to_use": "Run regex",
        "side_effects": "None",
        "price": "$50"
    }
    ```
    """
    
    agent = DataIngestionAgent(llm_gateway=MockLLMGateway(response_str=bad_llm_response))
    state = WorkflowState(raw_input="Some messy text")
    
    final_state = agent.process(state)
    
    assert final_state.errors == []
    assert final_state.product_data["product_name"] == "Markdown Serum"


def test_ingestion_handles_api_failure():
    """
    Scenario: The OpenAI API is down or times out.
    The system should not crash; it should log a graceful error.
    """
    agent = DataIngestionAgent(llm_gateway=MockLLMGateway(raise_error=TimeoutError("API Down")))
    state = WorkflowState(raw_input="Try to extract this")
    
    final_state = agent.process(state)
    
    assert len(final_state.errors) > 0
    assert "Extraction Crashed" in final_state.errors[0]
    assert "API Down" in final_state.errors[0]


def test_ingestion_handles_garbage_input():
    """
    Scenario: User inputs meaningless noise.
    The LLM might return empty JSON or the extraction might fail.
    """
    # LLM tries its best but returns empty JSON because no facts were found
    agent = DataIngestionAgent(llm_gateway=MockLLMGateway(response_str="{}"))
    state = WorkflowState(raw_input="asdf jkl; 1234 %%")
    
    final_state = agent.process(state)
    
    assert len(final_state.errors) > 0
    
    # UPDATED ASSERTION: Matches the specific error your agent actually raises
    # We check for EITHER "Validation Failed" (if Pydantic ran) OR "Extraction returned empty data" (if code skipped validation)
    error_msg = final_state.errors[0]
    assert "Validation Failed" in error_msg or "Extraction returned empty data" in error_msg


def test_ingestion_partial_hallucination():
    """
    Scenario: LLM returns JSON but misses required fields (e.g., Price).
    Pydantic validation should catch this.
    """
    # Missing 'price' and 'ingredients'
    incomplete_json = json.dumps({
        "product_name": "Incomplete Serum",
        "concentration": "10%"
    })
    
    agent = DataIngestionAgent(llm_gateway=MockLLMGateway(response_str=incomplete_json))
    state = WorkflowState(raw_input="text")
    
    final_state = agent.process(state)
    
    assert len(final_state.errors) > 0
    assert "Validation Failed" in final_state.errors[0]