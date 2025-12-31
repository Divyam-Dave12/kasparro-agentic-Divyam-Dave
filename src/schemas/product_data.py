from typing import List, Optional
from pydantic import BaseModel, Field, validator

class ProductData(BaseModel):
    # Required Fields (System needs these to function)
    product_name: str = Field(..., description="Name of the product")
    price: str = Field(..., description="Price with currency symbol")

    # Tolerant Fields (If AI misses them, default to generic text)
    concentration: str = Field(default="Standard", description="Concentration info")
    
    # We allow 'Optional' but default to a string so downstream code doesn't break
    skin_type: str = Field(default="All Skin Types", description="Target audience")
    how_to_use: str = Field(default="Follow package instructions.", description="Usage guide")
    side_effects: str = Field(default="None reported.", description="Safety warnings")
    
    key_ingredients: List[str] = Field(default_factory=list, description="List of ingredients")
    benefits: List[str] = Field(default_factory=list, description="List of benefits")

    # Validator to ensure we never have None even if the LLM sends explicit null
    @validator("skin_type", "how_to_use", "side_effects", "concentration", pre=True)
    def handle_nulls(cls, v):
        if v is None:
            return "Not specified"
        return str(v)

    @validator("key_ingredients", "benefits", pre=True)
    def handle_list_nulls(cls, v):
        if v is None:
            return []
        return v