from typing import List, Optional
from pydantic import BaseModel

class ProductData(BaseModel):
    product_name: str
    concentration: Optional[str] = None
    skin_type: str
    key_ingredients: List[str]
    benefits: List[str]
    how_to_use: str
    side_effects: str
    price: str