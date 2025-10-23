from app.models import Account
from app.models import db

from app.schemas.wallet_schemas import GetInitialAndCurrentSchema

def add_saving(user_id: int,validated: GetInitialAndCurrentSchema):
    new_saving=Account(  
    name = validated.name,
    currency = validated.currency ,
    initial_balance = validated.initial_balance ,
    current_balance = validated.current_balance,
    user_id=user_id
    )

    db.session.add(new_saving)
    db.session.commit()

    return new_saving




def update_saving(user_id: int, account_id: int, validated: GetInitialAndCurrentSchema):
    """Update an existing saving account belonging to the user."""
    saving = Account.query.filter_by(id=account_id, user_id=user_id).first()

    if not saving:
        raise ValueError("Saving account not found or doesn't belong to this user.")

    saving.name = validated.name
    saving.currency = validated.currency
    saving.initial_balance = validated.initial_balance
    saving.current_balance = validated.current_balance

    db.session.commit()
    return saving


def delete_saving(user_id: int, account_id: int):
    """Delete a saving account if it belongs to the current user."""
    saving = Account.query.filter_by(id=account_id, user_id=user_id).first()

    if not saving:
        raise ValueError("Saving account not found or doesn't belong to this user.")

    db.session.delete(saving)
    db.session.commit()

    return account_id

def get_all_accounts(user_id):
    all_accounts=Account.query.filter_by(user_id=user_id).all()
    if all_accounts:
        return all_accounts
    return None