from flask import Flask
from flask_jwt_extended import JWTManager
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    from app.extensions import jwt
    jwt.init_app(app)

    # Register blueprints
    from app.routes.web import web_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    return app