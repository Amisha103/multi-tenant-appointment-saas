from flask import Flask
from app.config import Config
from app.extensions import db, migrate, login_manager
from app.middlewares.tenant_middleware import load_current_business
from app.models.user import User
from flask_jwt_extended import JWTManager

jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # SQLAlchemy Engine Options (Recommended for Neon PostgreSQL)
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # JWT Configuration
    app.config["JWT_SECRET_KEY"] = "super-secret-key-for-multi-tenant-appointment-saas-project-2026"
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    jwt.init_app(app)

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import models
    from app import models

    # Create tables (Temporary)
    with app.app_context():
        db.create_all()

    # Register Blueprints
    from app.routes.landing_routes import landing_bp
    from app.routes.business_routes import business_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(landing_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(business_bp, url_prefix="/business")

    # Middleware
    app.before_request(load_current_business)

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))