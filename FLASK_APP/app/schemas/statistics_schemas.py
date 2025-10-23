from pydantic import BaseModel
from datetime import date


class GetOnlyDateSchema(BaseModel):
    end_prevision: date
    

class GetDaysPrevision(BaseModel):
    days: int