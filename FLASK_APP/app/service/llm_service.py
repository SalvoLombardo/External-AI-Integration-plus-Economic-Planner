from app.extensions import db
from app.models import PlannedTransaction, ActualTransaction
from app.enum_models import TransactionType


def get_all_outcome_info(user_id):
    transactions=PlannedTransaction.query.filter_by(user_id=user_id,transaction_type=TransactionType.OUTCOME).all()
    if not transactions:
        return None
    
    return [
        {
            "id": t.id,
            "title": t.title,
            "priority_score": t.priority_score,
            "planned_amount": t.planned_amount,
            "planned_date_start": t.planned_date_start.isoformat(),
            "planned_date_end": t.planned_date_end.isoformat() if t.planned_date_end else None,
            "category": t.category.name,
            "sub_category": t.sub_category.name
        }
        for t in transactions
    ]


