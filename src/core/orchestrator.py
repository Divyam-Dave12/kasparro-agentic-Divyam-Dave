from typing import Dict
from src.core.workflow_state import WorkflowState
from src.agents.base_agent import BaseAgent
from src.agents.supervisor import SupervisorAgent

class Orchestrator:
    def __init__(self, supervisor: SupervisorAgent, agents: Dict[str, BaseAgent]):
        self.supervisor = supervisor
        self.agents = agents

    def run(self, initial_state: WorkflowState) -> WorkflowState:
        state = initial_state
        print("🚀 Orchestrator Started (Dynamic Mode)")
        
        # Guard against infinite loops
        for _ in range(15):
            if state.is_complete:
                print("✅ System Finished.")
                break
                
            # 1. Supervisor Decides
            state = self.supervisor.process(state)
            next_agent_name = state.next_agent
            
            if next_agent_name == "FINISH":
                state.is_complete = True
                break
            
            # 2. Worker Executes
            print(f"👉 Supervisor chose: {next_agent_name}")
            worker = self.agents.get(next_agent_name)
            
            if worker:
                state = worker.process(state)
                state.last_agent = next_agent_name
            else:
                state.add_error(f"Unknown agent: {next_agent_name}")
                break
                
        return state