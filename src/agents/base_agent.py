from abc import ABC, abstractmethod
from src.core.workflow_state import WorkflowState

class BaseAgent(ABC):
    """
    Abstract Base Class defining the contract for all system agents.
    
    Design Philosophy:
    - Agents must be stateless logic units; all state is passed via WorkflowState.
    - Agents must implement the `process` method.
    - Agents should fail gracefully by updating state.errors rather than raising uncaught exceptions.
    """

    def __init__(self, agent_name: str):
        """
        Initialize the agent with a unique identifier.
        
        Args:
            agent_name (str): A descriptive name for logging and debugging.
        """
        self.agent_name = agent_name

    @abstractmethod
    def process(self, state: WorkflowState) -> WorkflowState:
        """
        Core logic method for the agent.
        
        Args:
            state (WorkflowState): The current snapshot of the workflow.
            
        Returns:
            WorkflowState: The updated state object after agent processing.
        """
        pass