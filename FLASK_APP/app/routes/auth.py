from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
from app.schemas.auth_schema import UserBaseSchema
from app.service.user_service import (
    username_is_taken, create_user_service, login_user_service, refresh_token_service
)

auth_bp = Blueprint("auth", __name__)
#-------------------------
#AUTH SECTION - New User - Login(jwt_token) - Refresh Token
#-------------------------
@auth_bp.post("/create_user")
def create_user():
    data = request.get_json()
    try:
        validated = UserBaseSchema(**data)
    except ValidationError as e:
        return jsonify({"Error": e.errors()}), 400

    if username_is_taken(validated):
        return jsonify({"Error": "User already exists"}), 409

    try:
        create_user_service(validated)
    except ValueError as e:
        return jsonify({"Error": str(e)}), 400

    return jsonify({"Success": "New user created"}), 200

@auth_bp.post("/login_user")
def login_user():
    data = request.get_json()
    try:
        validated = UserBaseSchema(**data)
    except ValidationError as e:
        return jsonify({"Error": e.errors()}), 400

    result = login_user_service(validated)
    if result is None:
        return jsonify({"Error": "Credenziali non valide"}), 401

    return jsonify(result), 200

@auth_bp.post("/refresh_token")
@jwt_required(refresh=True)
def refresh_access_token():
    user_id = get_jwt_identity()
    result = refresh_token_service(user_id)
    return jsonify(result), 200