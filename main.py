from src.core.workflow_state import WorkflowState
from src.core.orchestrator import Orchestrator
from src.agents.supervisor import SupervisorAgent
from src.agents.data_ingestion import DataIngestionAgent
from src.agents.researcher import ResearchAgent
from src.agents.drafter import DraftingAgent


RAW_INPUT = "Sell a Vitamin C Serum for $50."

def main():
    # 1. Initialize Workers
    registry = {
        "ingestor": DataIngestionAgent(),
        "researcher": ResearchAgent(),
        "drafter": DraftingAgent()
    }
    
    # 2. Initialize Boss
    supervisor = SupervisorAgent()
    
    # 3. Setup Orchestrator
    orchestrator = Orchestrator(supervisor, registry)
    
    # 4. Run
    state = WorkflowState(raw_input=RAW_INPUT)
    final_state = orchestrator.run(state)
    
    if final_state.errors:
        print("❌ Errors:", final_state.errors)
    else:
        print("✅ Success! Pages generated.")

if __name__ == "__main__":
    main()