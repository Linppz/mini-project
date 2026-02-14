from pydantic import BaseModel, Field
from typing import Optional
class FewShotExample(BaseModel):
    input: str
    output: str
    explanation: Optional[str] = Field(default = "")

class RenderResult(BaseModel):
    rendered_text : str
    token_count: int
    template_name : str
    variables_used : dict