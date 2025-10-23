from pydantic import BaseModel, field_validator

class UserBaseSchema(BaseModel):
    username: str
    password: str

    @field_validator("username")
    def username_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Username non può essere vuoto")
        return v.strip()