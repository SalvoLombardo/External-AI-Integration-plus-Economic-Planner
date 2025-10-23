from pydantic import BaseModel


class GetInitialAndCurrentSchema(BaseModel):
    initial_balance: float = 0.0
    current_balance: float = 0.0
    name: str
    currency: str = 'EUR'

    