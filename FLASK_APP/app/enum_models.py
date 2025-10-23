import enum
from .extensions import db

class TransactionType(enum.Enum):
    INCOME = "income"
    OUTCOME = "outcome"


class FrequencyEnum(enum.Enum):
    DAILY = "daily"
    WEEKLY= "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

