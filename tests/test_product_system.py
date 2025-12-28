import pytest
import json
from unittest.mock import MagicMock

from src.core.workflow_state import WorkflowState
from src.core.orchestrator import Orchestrator
from src.agents.data_ingestion import DataIngestionAgent
from src.agents.content_factory import ContentFactoryAgent

# --- MOCKS ---

class MockLLMGateway:
    """Simulates LLM responses for Extraction and Generation."""
    def __init__(self, responses=None):
        self.responses = responses or []
        self.call_count = 0

    def chat_completion(self, messages, temperature=0.0, response_format="json_object"):
        # Default behavior: Return empty JSON if out of responses
        if self.call_count >= len(self.responses):
            return "{}"
            
        resp = self.responses[self.call_count]
        self.call_count += 1
        return resp

# --- UNIT TESTS: DATA INGESTION ---

def test_ingestion_structured_data_success():
    """Test 1: Agent accepts valid structured data directly."""
    valid_data = {
        "product_name": "Test Serum",
        "concentration": "5%",
        "skin_type": "All",
        "key_ingredients": ["Water"],
        "benefits": ["Hydration"],
        "how_to_use": "Apply daily",
        "side_effects": "None",
        "price": "$10"
    }
    state = WorkflowState(product_data=valid_data)
    agent = DataIngestionAgent() # No LLM needed for structured data
    
    final_state = agent.process(state)
    
    assert final_state.errors == []
    assert final_state.product_data["product_name"] == "Test Serum"

def test_ingestion_raw_text_extraction():
    """Test 2: Agent calls LLM to extract JSON from raw text."""
    raw_text = "Sell a Vitamin C Serum for $20."
    
    # Simulate LLM extracting valid JSON from text
    mock_llm_response = json.dumps({
        "product_name": "Vitamin C Serum",
        "concentration": "10%",
        "skin_type": "Oily",
        "key_ingredients": ["Vit C"],
        "benefits": ["Brightening"],
        "how_to_use": "Apply daily",
        "side_effects": "Tingling",
        "price": "$20"
    })
    
    agent = DataIngestionAgent(llm_gateway=MockLLMGateway([mock_llm_response]))
    state = WorkflowState(raw_input=raw_text)
    
    final_state = agent.process(state)
    
    assert final_state.errors == []
    assert final_state.product_data["price"] == "$20"

def test_ingestion_validation_failure():
    """Test 3: Schema validation catches missing fields."""
    # LLM returns incomplete data (missing 'price')
    incomplete_response = json.dumps({
        "product_name": "Bad Product"
        # Missing other required fields
    })
    
    agent = DataIngestionAgent(llm_gateway=MockLLMGateway([incomplete_response]))
    state = WorkflowState(raw_input="some text")
    
    final_state = agent.process(state)
    
    assert len(final_state.errors) > 0
    assert "Validation Failed" in final_state.errors[0] or "Schema" in final_state.errors[0]

# --- UNIT TESTS: CONTENT FACTORY ---

def test_content_factory_success():
    """Test 4: Factory generates all 3 pages given valid product data."""
    valid_data = {
        "product_name": "Test Serum",
        "concentration": "5%",
        "skin_type": "All",
        "key_ingredients": ["Water"],
        "benefits": ["Hydration"],
        "how_to_use": "Apply daily",
        "side_effects": "None",
        "price": "$10"
    }
    
    # We need to mock 5 LLM calls:
    # 1. Competitor Gen
    # 2. Question Gen
    # 3. Product Description (for Product Page)
    # 4. FAQ Answers (for FAQ Page)
    # 5. (Comparison Page uses pure logic, no LLM call usually, or mock if needed)
    
    responses = [
        json.dumps({"product_name": "Comp B", "price": "$15", "key_ingredients": [], "benefits": []}), # Competitor
        json.dumps({"questions": ["Q1", "Q2"]}), # Questions
        json.dumps({"description": "Great product"}), # Product Page Desc
        json.dumps({"faqs": [{"question": "Q1", "answer": "A1"}]}), # FAQ Answers
    ]
    
    agent = ContentFactoryAgent(llm_gateway=MockLLMGateway(responses))
    state = WorkflowState(product_data=valid_data)
    
    final_state = agent.process(state)
    
    assert final_state.errors == []
    assert final_state.competitor_data["product_name"] == "Comp B"
    assert final_state.product_page["meta"]["price"] == "$10"
    assert final_state.faq_page["data"][0]["question"] == "Q1"
    assert final_state.comparison_page["title"] == "Test Serum vs Comp B"

# --- INTEGRATION TEST: FULL PIPELINE ---

def test_integration_full_flow():
    """Test 5: Raw Text -> Ingestion -> Factory -> JSON Files."""
    
    raw_input = "Selling Glow Serum for $50."
    
    # Sequence of ALL LLM calls across agents:
    # 1. Ingestion: Extraction
    # 2. Factory: Competitor
    # 3. Factory: Questions
    # 4. Factory: Product Desc
    # 5. Factory: FAQ Answers
    
    all_responses = [
        # 1. Extraction Result
        json.dumps({
            "product_name": "Glow Serum",
            "concentration": "10%",
            "skin_type": "All",
            "key_ingredients": ["Gold"],
            "benefits": ["Glow"],
            "how_to_use": "Daily",
            "side_effects": "None",
            "price": "$50"
        }),
        # 2. Competitor
        json.dumps({"product_name": "Dull Serum", "price": "$100", "key_ingredients": [], "benefits": []}),
        # 3. Questions
        json.dumps({"questions": ["Is it safe?"]}),
        # 4. Product Desc
        json.dumps({"description": "It glows."}),
        # 5. FAQ Answers
        json.dumps({"faqs": [{"question": "Is it safe?", "answer": "Yes"}]})
    ]
    
    # Setup Agents with shared Mock Gateway
    mock_gateway = MockLLMGateway(all_responses)
    agents = [
        DataIngestionAgent(llm_gateway=mock_gateway),
        ContentFactoryAgent(llm_gateway=mock_gateway)
    ]
    
    orchestrator = Orchestrator(agents)
    state = WorkflowState(raw_input=raw_input)
    
    final_state = orchestrator.run(state)
    
    assert final_state.errors == []
    # Verify end-to-end data transformation
    assert final_state.product_data["product_name"] == "Glow Serum"
    assert final_state.product_page["content"]["headline"] == "Discover Glow Serum"