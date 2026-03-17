from pydantic import BaseModel
from typing import Optional

class ProductInput(BaseModel):
    name: str
    description: Optional[str] = ""
    image_url: Optional[str] = ""

class MatchRequest(BaseModel):
    product_a: ProductInput
    product_b: ProductInput

class MatchResponse(BaseModel):
    product_a:    str
    product_b:    str
    fuzzy_score:  float
    text_sim:     float
    image_sim:    float
    final_score:  float
    is_duplicate: bool