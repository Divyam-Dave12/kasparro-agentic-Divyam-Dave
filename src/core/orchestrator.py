from typing import Dict
from src.core.workflow_state import WorkflowState
from src.agents.base_agent import BaseAgent
from src.agents.supervisor import SupervisorAgent
from src.Utils.logger import RunLogger

class Orchestrator:
    def __init__(self, supervisor: SupervisorAgent, agents: Dict[str, BaseAgent]):
        self.supervisor = supervisor
        self.agents = agents
        self.logger = RunLogger()

    def run(self, initial_state: WorkflowState) -> WorkflowState:
        state = initial_state
        print("Orchestrator Started (Dynamic Mode)")
        self.logger.log_step("Orchestrator", "Startup", "Initializing Dynamic Workflow")

        steps = 0
        MAX_STEPS = 15

        while not state.is_complete and steps < MAX_STEPS:
            # 1. Supervisor Decision
            state = self.supervisor.process(state)
            
            if state.is_complete:
                self.logger.log_step("Supervisor", "Decision", " signaled COMPLETION.")
                break

            # 2. Log the choice
            next_agent = state.next_agent
            self.logger.log_step("Supervisor", "Routing", f"delegated task to `{next_agent}`")

            # 3. Execute Agent
            agent = self.agents.get(next_agent)
            if agent:
                try:
                    state = agent.process(state)
                    self.logger.log_step(next_agent, "Success", "Task completed")
                    
                    # Special log if feedback was given
                    if state.errors and "ReviewFeedback" in state.errors[-1]:
                         self.logger.log_step(next_agent, "⚠️ Issue Detected", "Triggered Self-Correction")
                         
                except Exception as e:
                    self.logger.log_step(next_agent, "CRITICAL ERROR", str(e))
                    state.add_error(str(e))
            
            steps += 1
            
        self.logger.save_report()
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