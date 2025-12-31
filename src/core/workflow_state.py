from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class WorkflowState(BaseModel):
    # --- INPUTS ---
    raw_input: Optional[str] = None
    product_data: Dict[str, Any] = Field(default_factory=dict)
    
    # --- INTERMEDIATE DATA ---
    competitor_data: Optional[Dict[str, Any]] = None
    generated_questions: List[str] = Field(default_factory=list)

    # --- OUTPUTS ---
    faq_page: Optional[Dict[str, Any]] = None
    product_page: Optional[Dict[str, Any]] = None
    comparison_page: Optional[Dict[str, Any]] = None
    
    # --- CONTROL FLOW (NEW) ---
    last_agent: Optional[str] = None
    next_agent: Optional[str] = None
    is_complete: bool = False
    
    # --- METADATA ---
    errors: List[str] = Field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)