from typing import List
from src.core.workflow_state import WorkflowState
from src.agents.base_agent import BaseAgent

class Orchestrator:
    """
    Minimal Control Flow Manager.
    
    Responsibilities:
    1. Holds the registry of agents to execute.
    2. Passes state sequentially from one agent to the next.
    3. Enforces early stopping if the state encounters critical errors.
    """

    def __init__(self, agents: List[BaseAgent]):
        """
        Initialize the orchestrator with a defined pipeline of agents.
        
        Args:
            agents (List[BaseAgent]): Ordered list of agents to execute.
        """
        self.agents = agents

    def run(self, initial_state: WorkflowState) -> WorkflowState:
        """
        Executes the workflow pipeline.
        
        Args:
            initial_state (WorkflowState): The starting state with raw user input.
            
        Returns:
            WorkflowState: The final state after all agents have run or an error occurred.
        """
        current_state = initial_state

        for agent in self.agents:
            # Circuit breaker: Stop execution if previous steps failed
            if current_state.errors:
                print(f"Orchestrator: Stopping execution due to errors before {agent.agent_name}.")
                break
            
            # Execute agent logic
            # Note: In a real production system, this would be wrapped in try/except 
            # to catch unexpected crashes and log them to state.errors.
            current_state = agent.process(current_state)

        return current_state