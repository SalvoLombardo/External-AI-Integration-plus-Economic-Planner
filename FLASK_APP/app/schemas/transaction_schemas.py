from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date


from enum import Enum

class TransactionTypeEnum(str, Enum):
    income = 'income'
    outcome = 'outcome'

class FrequencyEnum(str, Enum):
    daily = 'daily'
    weekly = 'weekly'
    monthly = 'monthly'
    yearly = 'yearly'




class TransactionIdOnlySchema(BaseModel):
    id: int




from app.enum_models import FrequencyEnum,TransactionType

# I'm calling the Enum type and pass the value, e.g. Transaction type has 'income' and 'outcome'
# and they are passed into a variable, to be used in @field_validator
transaction_type_values = [e.value for e in TransactionType]
frequency_values = [e.value for e in FrequencyEnum]


#-------------------------------
#CREATION-CONFIRMATION
#-------------------------------
class NewPlannedTransactionSchema(BaseModel):
    title: str
    planned_amount: int
    planned_date_start: Optional[date] = date.today()
    planned_date_end: Optional[date] = None
    transaction_type: str
    frequency: Optional[str] = None
    recurring: bool = False
    priority_score: int = Field(..., ge=1, le=3) #the score must be ge(greater then) and le(lessthen)

    

    category_name: str | None = None
    sub_category_name: str | None = None

    side_project_id: Optional[int] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    account_id: Optional[int] = None

    # Validators
    @field_validator('transaction_type')
    def validate_transaction_type(cls, v):
        if v not in transaction_type_values:
            raise ValueError(f'transaction_type must be one of {transaction_type_values}')
        return v

    @field_validator('frequency')
    def validate_frequency(cls, v):
        if v is not None and v not in frequency_values:
            raise ValueError(f'frequency must be one of {frequency_values}')
        return v

class ModifiedTransactionSchema(NewPlannedTransactionSchema):
    planned_id: int



#-------------------------------
#UPDATE
#-------------------------------
class UpdatePlannedTransactionSchema(BaseModel):
    id: int
    title: Optional[str] = None
    planned_amount: Optional[int] = None
    planned_date_start: Optional[date] = None
    planned_date_end: Optional[date] = None
    transaction_type: Optional[str] = None
    frequency: Optional[str] = None
    recurring: Optional[bool] = None
    priority_score: Optional[int] = None

    category_name: Optional[str] = None
    sub_category_name: Optional[str] = None
    side_project_id: Optional[int] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    account_id: Optional[int] = None

    # stessi validator
    @field_validator('transaction_type')
    def validate_transaction_type(cls, v):
        if v is not None and v not in transaction_type_values:
            raise ValueError(f'transaction_type must be one of {transaction_type_values}')
        return v

    @field_validator('frequency')
    def validate_frequency(cls, v):
        if v is not None and v not in frequency_values:
            raise ValueError(f'frequency must be one of {frequency_values}')
        return v

class UpdateActualTransactionSchema(BaseModel):
    id: int
    title: Optional[str] = None
    actual_amount: Optional[int] = None
    actual_date_start: Optional[date] = None
    actual_date_end: Optional[date] = None
    transaction_type: Optional[str] = None
    frequency: Optional[str] = None
    recurring: Optional[bool] = None
    priority_score: Optional[int] = None

    category_name: Optional[str] = None
    sub_category_name: Optional[str] = None
    side_project_id: Optional[int] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    account_id: Optional[int] = None

    # stessi validator
    @field_validator('transaction_type')
    def validate_transaction_type(cls, v):
        if v is not None and v not in transaction_type_values:
            raise ValueError(f'transaction_type must be one of {transaction_type_values}')
        return v

    @field_validator('frequency')
    def validate_frequency(cls, v):
        if v is not None and v not in frequency_values:
            raise ValueError(f'frequency must be one of {frequency_values}')
        return v


