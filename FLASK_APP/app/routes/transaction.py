from app.extensions import db
from flask import Blueprint, request, jsonify
from app.service.category_subcategory_service import get_or_create_category, get_or_create_sub_category
from app.service.transaction_service import (
    create_new_trans, get_planned_and_save_as_actual, 
    save_modified_trans, is_completed_true, delete_planned_func , 
    delete_actual_func ,check_if_completed, get_single_actual_trans, 
    get_single_planned_trans,update_planned_transaction_service,update_actual_transaction_service
    )
from flask_jwt_extended import jwt_required, get_jwt_identity

#importing Schemas and decoratort
#using a decorator to have an easy way to aplly the pydantic validation and 
#call request.get_json()in a direct way
from app.utils.decorators import validate_input 
from app.schemas.transaction_schemas import NewPlannedTransactionSchema, ModifiedTransactionSchema ,TransactionIdOnlySchema, UpdatePlannedTransactionSchema ,UpdateActualTransactionSchema
from pydantic import ValidationError

transaction_bp = Blueprint('transaction', __name__)




####################### (--IMPORTANT--)
# HOW TRANSACTIONS WORKS
#   There are two type of transaction: 1. Planned 2. Actual
#   A planned is something that can happen and with uncertain value, a planned can
#   becoma an Actual trasaction, it means that the old transaction get stored in the db
#   whit the same data or with some new/modified data, in fact planned_transaction has a field in db called
#   'is_completed', when the function save the new Actual_transaction this field become = False
#   useful for some selection e to not repeat some data.



#-------------------------------
#CREATION-CONFIRMATION
#-------------------------------

@transaction_bp.post('/new_planned_transaction')
@jwt_required()
@validate_input(NewPlannedTransactionSchema)
def new_planned_transaction(payload: NewPlannedTransactionSchema):
    user_id = int(get_jwt_identity())

    
    if payload.category_id:
        category_id = payload.category_id
    else:
        category_id = get_or_create_category(user_id, payload.model_dump())  # usa model_dump() invece di dict()

    if payload.sub_category_id:
        sub_category_id = payload.sub_category_id
    else:
        sub_category_id = get_or_create_sub_category(category_id, payload.model_dump())

    new_transaction = create_new_trans(payload, user_id, category_id, sub_category_id)

    return jsonify({'success': True, 'planned_transaction_id': new_transaction.id}), 201

@transaction_bp.post('/confirm_transaction')
@jwt_required()
def confirm_transaction():
    #Here i can riceve only 2 cases:
    # 1-Only an id of a planned transaction, whitch become an Actual as it is
    # 2-A modified trans dict where there are the new info about transaction,
    # and save only the new info
    #Validation: I use ydantic here just to validate only modified_trans because
    # the id is alreay safe


    data = request.get_json() or {}
    user_id = int(get_jwt_identity())

    planned_id = data.get('id')
    if not planned_id:
        return jsonify({'error': 'planned_id (id) missing'}), 400

    # Check if already completed
    if check_if_completed(planned_id):
        return jsonify({'error': 'Planned transaction already completed'}), 400

    # Check for modified data
    modified_trans = data.get('modified_trans')

    if modified_trans:
        #Adding the id to the Json to be exact as the ModifiedTransactionSchema requires
        modified_trans['planned_id']=planned_id
        
        
        try:
            validated = ModifiedTransactionSchema(**modified_trans)
        except ValidationError as e:
            return jsonify({'errors': e.errors()}), 400

        actual_trans = save_modified_trans(user_id, validated)
        return jsonify({'success': True, 'actual_transaction_id': actual_trans.id}), 201
    
    # Otherwise, clone the planned transaction as is
    actual_trans = get_planned_and_save_as_actual(user_id, planned_id)
    if actual_trans:
        return jsonify({'success': True, 'actual_transaction_id': actual_trans.id}), 200

    return jsonify({'error': 'Planned transaction not found'}), 404





#-------------------------------
#SEARCH
#-------------------------------
@transaction_bp.post('/search_planned_transaction')
@jwt_required()
def search_planned_transaction():
    user_id=int(get_jwt_identity())
    data= request.get_json()

    try:
        validation=TransactionIdOnlySchema(**data)

    except ValidationError as e:
        return jsonify({'errors': e.errors()}),400
    
    searched_trans=get_single_planned_trans(user_id,validation)

    if not searched_trans:
        return jsonify({'error': 'Planned transaction not found'}), 404

    transaction_dict = {
        "id": searched_trans.id,
        "title": searched_trans.title,
        "planned_amount": searched_trans.planned_amount,
        "planned_date_start": searched_trans.planned_date_start.isoformat() if searched_trans.planned_date_start else None,
        "transaction_type": searched_trans.transaction_type.value if hasattr(searched_trans.transaction_type, "value") else str(searched_trans.transaction_type),
        "priority_score": searched_trans.priority_score.value if hasattr(searched_trans.priority_score, "value") else searched_trans.priority_score,
        "is_completed": searched_trans.is_completed,
        "category": searched_trans.category.name if searched_trans.category else None,
        "sub_category": searched_trans.sub_category.name if searched_trans.sub_category else None,
        "recurring": searched_trans.recurring,
        "frequency": searched_trans.frequency.value if hasattr(searched_trans.frequency, "value") else str(searched_trans.frequency),    
    }

    return jsonify({'success': True, 'transaction': transaction_dict}), 200
    

@transaction_bp.post('/search_actual_transaction')
@jwt_required()
def search_actual_transaction():
    user_id=int(get_jwt_identity())
    data= request.get_json()

    try:
        validation=TransactionIdOnlySchema(**data)

    except ValidationError as e:
        return jsonify({'errors': e.errors()}),400
    
    searched_trans=get_single_actual_trans(user_id,validation)

    if not searched_trans:
        return jsonify({'error': 'Planned transaction not found'}), 404

    
    return jsonify({'success': True, 'transaction': searched_trans.to_dict()}), 200








#-------------------------------
#UPDATE
#-------------------------------
@transaction_bp.post('/update_planned_transaction')
@jwt_required()
def update_planned_transaction():
    user_id=int(get_jwt_identity())
    data=request.get_json()

    try:
        validated=UpdatePlannedTransactionSchema(**data)
    except ValidationError as e:
        return jsonify({'Error': e.errors()}),400
    

    updated_transaction=update_planned_transaction_service(user_id,validated)

    if not updated_transaction:
        return jsonify({'Error': "Update failed"}),400
    
    return jsonify({'Success': 'Updated'})

@transaction_bp.post('/update_actual_transaction')
@jwt_required()
def update_actual_transaction():
    user_id=int(get_jwt_identity())
    data=request.get_json()

    try:
        validated=UpdateActualTransactionSchema(**data)
    except ValidationError as e:
        return jsonify({'Error': e.errors()}),400
    

    updated_transaction=update_actual_transaction_service(user_id,validated)

    if not updated_transaction:
        return jsonify({'Error': "Update failed"}),400
    
    return jsonify({'Success': 'Updated'})
    
    








#-------------------------------
#DELETE
#-------------------------------
@transaction_bp.post('/delete_planned_transaction')
@jwt_required()
def delete_planned_transaction():
    data = request.get_json() or {}
    user_id = int(get_jwt_identity())
    
    #Pydantic Validation
    try:
        validated = TransactionIdOnlySchema(**data)
    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 400

    deleted_element = delete_planned_func(validated, user_id)
    
    if not deleted_element:
        return jsonify({'error': 'Actual transaction not found'}), 404
    
    return jsonify({
        'success': True,
        'deleted_actual_transaction_id': deleted_element.id
    }), 200

    
@transaction_bp.post('/delete_actual_transaction')
@jwt_required()
def delete_actual_transaction():
    data = request.get_json() or {}
    user_id = int(get_jwt_identity())
    
    #Pydantic Validation
    try:
        validated = TransactionIdOnlySchema(**data)
    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 400

    deleted_element = delete_actual_func(validated, user_id)
    
    if not deleted_element:
        return jsonify({'error': 'Actual transaction not found'}), 404
    
    return jsonify({
        'success': True,
        'deleted_actual_transaction_id': deleted_element.id
    }), 200
    


