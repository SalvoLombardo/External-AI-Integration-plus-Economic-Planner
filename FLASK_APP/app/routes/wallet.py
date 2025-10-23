from app.extensions import db
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.service.wallet_service import add_saving, update_saving, delete_saving

from app.schemas.wallet_schemas import GetInitialAndCurrentSchema
from app.schemas.wallet_schemas import GetInitialAndCurrentSchema
from pydantic import ValidationError


wallet_bp = Blueprint('wallet_bp', __name__)

@wallet_bp.post("/create_new_saving")
@jwt_required()
def create_new_saving():
    data=request.get_json()

    user_id = int(get_jwt_identity())


    try:
        validated=GetInitialAndCurrentSchema(**data)
    except ValidationError as e:
        return jsonify({'Error': e.errors()}),400
    
    
    try:
        new_saving = add_saving(user_id, validated)
    except Exception as e:
        return jsonify({'error': f'Could not create saving: {str(e)}'}), 500
    
    return jsonify({'success': True, 'Created new saving': new_saving.id}), 201





@wallet_bp.put("/update_saving/<int:account_id>")
@jwt_required()
def update_saving_route(account_id):
    """Update an existing account for the authenticated user."""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    try:
        validated = GetInitialAndCurrentSchema(**data)
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400

    try:
        updated_saving = update_saving(user_id, account_id, validated)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Could not update saving: {str(e)}'}), 500

    return jsonify({
        'success': True,
        'updated_saving': {
            'id': updated_saving.id,
            'name': updated_saving.name,
            'currency': updated_saving.currency,
            'initial_balance': updated_saving.initial_balance,
            'current_balance': updated_saving.current_balance
        }
    }), 200



@wallet_bp.delete("/delete_saving/<int:account_id>")
@jwt_required()
def delete_saving_route(account_id):
    """Delete an account belonging to the authenticated user."""
    user_id = int(get_jwt_identity())

    try:
        deleted_id = delete_saving(user_id, account_id)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Could not delete saving: {str(e)}'}), 500

    return jsonify({'success': True, 'deleted_saving_id': deleted_id}), 200


   