from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime



class FewShotExample(BaseModel):
    input: str
    output: str
    explanation: Optional[str] = Field(default = "")

class RenderResult(BaseModel):
    rendered_text : str
    token_count: int
    template_name : str
    variables_used : dict

#单个prompt的记录
class PromptAuditLog(BaseModel):
    template_name: str
    version_hash: str
    rendered_prompt: str
    variables: dict
    timestamp: datetime = Field(default_factory = datetime.now)



#单个模板的记录

class PromptVersion(BaseModel):
    template_name: str
    version_hash: str
    rendered_text: str
    timestamp: datetime = Field(default_factory = datetime.now)