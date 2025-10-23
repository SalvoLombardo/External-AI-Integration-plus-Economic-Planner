from flask import  Flask
from app.extensions import db,migrate,jwt

from app.routes.transaction import transaction_bp
from app.routes.auth import auth_bp
from app.routes.statistics import statistics
from app.routes.wallet import wallet_bp

import os
from dotenv import load_dotenv



load_dotenv()

def create_app():
    app=Flask(__name__)

    

    app.config['SQLALCHEMY_DATABASE_URI']=os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SECRET_KEY']=os.getenv('SECRET_KEY')
    app.config["JWT_SECRET_KEY"]=os.getenv('JWT_SECRET_KEY')

    db.init_app(app)
    migrate.init_app(app,db)
    jwt.init_app(app)


    app.register_blueprint(transaction_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(statistics)
    app.register_blueprint(wallet_bp)
    


    return app