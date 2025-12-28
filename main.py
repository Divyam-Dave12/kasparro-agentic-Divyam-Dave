import json
import os
from src.core.orchestrator import Orchestrator
from src.core.workflow_state import WorkflowState
from src.agents.data_ingestion import DataIngestionAgent
from src.agents.content_factory import ContentFactoryAgent

# 1. Product Data (From Assignment)
GLOWBOOST_DATA = {
    "product_name": "GlowBoost Vitamin C Serum",
    "concentration": "10% Vitamin C",
    "skin_type": "Oily, Combination",
    "key_ingredients": ["Vitamin C", "Hyaluronic Acid"],
    "benefits": ["Brightening", "Fades dark spots"],
    "how_to_use": "Apply 2–3 drops in the morning before sunscreen",
    "side_effects": "Mild tingling for sensitive skin",
    "price": "₹699"
}

def save_json(filename: str, data: dict):
    """Helper to save clean JSON artifacts."""
    if not data:
        print(f"⚠️ Warning: No data to save for {filename}")
        return
        
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved: {filename}")

def main():
    print("🚀 Starting Agentic Content System...")
    
    # 2. Initialize State with Raw Data
    initial_state = WorkflowState(product_data=GLOWBOOST_DATA)

    # 3. Define Pipeline (The Graph)
    # Data Ingestion -> Content Factory (Generates all pages)
    agents = [
        DataIngestionAgent(),
        ContentFactoryAgent() 
    ]

    orchestrator = Orchestrator(agents=agents)

    # 4. Run Pipeline
    final_state = orchestrator.run(initial_state)

    # 5. Check for System Errors
    if final_state.errors:
        print("\n❌ Pipeline Failed with Errors:")
        for err in final_state.errors:
            print(f" - {err}")
        return

    # 6. Export Artifacts (Requirement 6)
    print("\n📦 Exporting Content Pages...")
    save_json("product_page.json", final_state.product_page)
    save_json("faq.json", final_state.faq_page)
    save_json("comparison_page.json", final_state.comparison_page)

    print("\n✨ System Execution Complete.")

if __name__ == "__main__":
    main()