from flask import jsonify
import datetime

#Importing db, models and enum
from app.extensions import db
from app.models import PlannedTransaction, ActualTransaction
from app.enum_models import TransactionType, FrequencyEnum

#Importing validation schemas from pydantic
from app.schemas.transaction_schemas import NewPlannedTransactionSchema, TransactionIdOnlySchema ,UpdatePlannedTransactionSchema, UpdateActualTransactionSchema




def _parse_date_optional(value):
    if not value:
        return None
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.date() if isinstance(value, datetime.datetime) else value
    # expect ISO format 'YYYY-MM-DD'
    try:
        return datetime.date.fromisoformat(value)
    except Exception:
        return None




def create_new_trans(payload: NewPlannedTransactionSchema, user_id: int, category_id: int, sub_category_id: int):
    planned_transaction = PlannedTransaction(
        title=payload.title,
        planned_amount=payload.planned_amount,
        planned_date_start=payload.planned_date_start or datetime.date.today(),
        planned_date_end=payload.planned_date_end,
        transaction_type=payload.transaction_type,
        frequency=payload.frequency,
        recurring=payload.recurring,
        priority_score=payload.priority_score,
        user_id=user_id,
        category_id=category_id,
        sub_category_id=sub_category_id,
        side_project_id=payload.side_project_id
    )

    db.session.add(planned_transaction)
    db.session.commit()
    return planned_transaction

def get_planned_and_save_as_actual(user_id, trans_id):
    # Cerca solo transazioni non completate
    planned_transaction = PlannedTransaction.query.filter_by(
        id=trans_id,
        is_completed=False
    ).first()
    
    if not planned_transaction:
        return None  # Non esiste o è completata

    actual_transaction = ActualTransaction(
        title=planned_transaction.title,
        actual_amount=planned_transaction.planned_amount,
        actual_date_start=planned_transaction.planned_date_start,
        actual_date_end=planned_transaction.planned_date_end,
        transaction_type=planned_transaction.transaction_type,
        frequency=planned_transaction.frequency,
        recurring=planned_transaction.recurring,
        priority_score=planned_transaction.priority_score,
        planned_id=planned_transaction.id,
        user_id=user_id,
        category_id=planned_transaction.category_id,
        sub_category_id=planned_transaction.sub_category_id,
        side_project_id=planned_transaction.side_project_id
    )

    # Aggiorna lo stato della PlannedTransaction
    planned_transaction.is_completed = True

    db.session.add(actual_transaction)
    db.session.commit()
    return actual_transaction

def save_modified_trans(user_id, validated_data):
    # If the client sends a modified transaction (not from a planned), accept fields
    title = validated_data.title
    # prefer actual_amount if provided, otherwise choose  planned_amount 
    actual_amount = validated_data.planned_amount if validated_data.planned_amount is not None else validated_data.planned_amount
    actual_date_start = validated_data.planned_date_start or datetime.date.today()
    actual_date_end = validated_data.planned_date_end

    transaction_type = validated_data.transaction_type
    frequency = validated_data.frequency
    recurring = validated_data.recurring    
    priority_score = validated_data.priority_score or 1
    planned_id = validated_data.planned_id  
    category_id = validated_data.category_id
    sub_category_id = validated_data.sub_category_id
    side_project_id = validated_data.side_project_id

    actual_transaction = ActualTransaction(
        title=title,
        actual_amount=actual_amount,
        actual_date_start=actual_date_start,
        actual_date_end=actual_date_end,
        transaction_type=transaction_type,
        frequency=frequency,
        recurring=recurring,
        priority_score=priority_score,
        planned_id=planned_id,
        user_id=user_id,
        category_id=category_id,
        sub_category_id=sub_category_id,
        side_project_id=side_project_id
    )

    db.session.add(actual_transaction)
    db.session.commit()

    return actual_transaction


def check_if_completed(planned_id):
    planned_trans=PlannedTransaction.query.filter_by(id=planned_id).first()

    if planned_trans.is_completed==True:
        return planned_trans
    else:
        return None

def is_completed_true(planned_id):
    plannned_trans=PlannedTransaction.query.get(planned_id)

    if not plannned_trans:
        return None
    plannned_trans.is_completed=True
    db.session.commit()


    return plannned_trans




def get_all_plann_trans(user_id):
    all_trans=PlannedTransaction.query.filter_by(user_id=user_id).all() or []

    if all_trans:
        return all_trans
    else:
        return None

def get_all_actual_trans(user_id):
    all_trans=ActualTransaction.query.filter_by(user_id=user_id).all()

    if all_trans:
        return all_trans
    else:
        return None

def get_all_trans(user_id: int):
    planned = get_all_plann_trans(user_id)
    actual = get_all_actual_trans(user_id)
    return (planned or []) + (actual or [])





def get_single_planned_trans(user_id:int,planned_id: TransactionIdOnlySchema):
    planned_transaction = PlannedTransaction.query.filter_by(id=planned_id.id,user_id=user_id).first()
    
    if not planned_transaction:
        return None
    
    return planned_transaction

def get_single_actual_trans(user_id: int,planned_id:TransactionIdOnlySchema):
    actual_transaction = ActualTransaction.query.filter_by(id=planned_id.id,user_id=user_id).first()
    
    if not actual_transaction:
        return None
    
    return actual_transaction






def update_planned_transaction_service(user_id: int, validated_data: UpdatePlannedTransactionSchema):
    planned_transaction = PlannedTransaction.query.filter_by(id=validated_data.id, user_id=user_id).first()

    if not planned_transaction:
        return None

    #Here with model_dump, i convert validated data, originally a Pydantic model
    # in a dict, with exclude_unset (means only set data will be stored in the dict)
    # and for more security i use hasattr and then -> setattr
    for field, value in validated_data.model_dump(exclude_unset=True).items():
        if hasattr(planned_transaction, field) and value is not None:
            setattr(planned_transaction, field, value)

    db.session.commit()
    return planned_transaction

def update_actual_transaction_service(user_id: int, validated_data: UpdateActualTransactionSchema):
    actual_transaction = ActualTransaction.query.filter_by(id=validated_data.id, user_id=user_id).first()

    if not actual_transaction:
        return None

    #Here with model_dump, i convert validated data, originally a Pydantic model
    # in a dict, with exclude_unset (means only set data will be stored in the dict)
    # and for more security i use hasattr and then -> setattr
    for field, value in validated_data.model_dump(exclude_unset=True).items():
        if hasattr(actual_transaction, field) and value is not None:
            setattr(actual_transaction, field, value)

    db.session.commit()
    return actual_transaction


      






def delete_planned_func(validated: TransactionIdOnlySchema, user_id : int):

    planned_transaction = PlannedTransaction.query.filter_by(id=validated.id,user_id=user_id).first()
    
    if not planned_transaction:
        return None
    
    db.session.delete(planned_transaction)
    db.session.commit()

    return planned_transaction

def delete_actual_func(validated: TransactionIdOnlySchema, user_id: int):
    actual_transaction = ActualTransaction.query.filter_by(
        id=validated.id,
        user_id=user_id
    ).first()
    
    if not actual_transaction:
        return None
    
    db.session.delete(actual_transaction)
    db.session.commit()

    return actual_transaction

