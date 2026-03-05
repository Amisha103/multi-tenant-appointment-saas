from flask import Flask
from app.config import Config
from app.extensions import db, migrate, login_manager
from app.middlewares.tenant_middleware import load_current_business
from app.models.user import User
from flask_jwt_extended import JWTManager

jwt = JWTManager()


def create_app():
    app = Flask(__name__)

  
    app.config.from_object(Config)

 
    app.config["JWT_SECRET_KEY"] = "super-secret-key-for-multi-tenant-appointment-saas-project-2026"

   
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

 
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    jwt.init_app(app)


    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)


    from app import models


    from app.routes.landing_routes import landing_bp
    from app.routes.business_routes import business_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(landing_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(business_bp, url_prefix="/business")

 
    app.before_request(load_current_business)

    return app



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))