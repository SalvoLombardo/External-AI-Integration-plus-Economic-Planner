from app.models import User
from app.extensions import bcrypt,db
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
import re





def hash_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("La password deve essere di almeno 8 caratteri")
    if not re.search(r"[A-Z]", password):
        raise ValueError("La password deve contenere almeno una lettera maiuscola")
    if not re.search(r"[0-9]", password):
        raise ValueError("La password deve contenere almeno un numero")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("La password deve contenere almeno un simbolo speciale")
    
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    return hashed

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.check_password_hash(hashed, password)



def username_is_taken(validated):
    return User.query.filter_by(username=validated.username).first() is not None

def create_user_service(validated):
    hashed_password = hash_password(validated.password)
    user = User(username=validated.username, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return user

def login_user_service(validated):
    user = User.query.filter_by(username=validated.username.strip()).first()
    if not user or not verify_password(validated.password, user.password):
        return None

    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(minutes=60))
    refresh_token = create_refresh_token(identity=str(user.id))

    return {"access_token": access_token, "refresh_token": refresh_token}

def refresh_token_service(user_id):
    new_access_token = create_access_token(identity=user_id, expires_delta=timedelta(minutes=60))
    new_refresh_token = create_refresh_token(identity=user_id)
    return {"access_token": new_access_token, "refresh_token": new_refresh_token}


