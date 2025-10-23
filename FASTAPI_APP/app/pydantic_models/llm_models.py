# app/pydantic_models/llm_models.py
from pydantic import BaseModel, field_validator
from typing import Dict, Any

class LLMRequest(BaseModel):
    text: str

class LLMResponse(BaseModel):
    processed_text: str



#I use data: Dict[str, Any] = {}  to cover all the possibility because the type of input will be alway different based
#on what Flask endpoint ask
class UserTokenTaskDataSchema(BaseModel):
    user_jwt_token: str
    task: str
    data: Dict[str, Any] = {}  

    @field_validator("user_jwt_token")
    def strip_token(cls, v):
        return v.strip() if v else v
