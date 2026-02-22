from flask import Flask
from app.config import Config
from app.extensions import db, migrate
from app.middlewares.tenant_middleware import load_current_business

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    
    db.init_app(app)
    migrate.init_app(app, db)
    from app import models

    
    
    from app.routes.landing_routes import landing_bp
    from app.routes.business_routes import business_bp

    
    app.register_blueprint(landing_bp)
    app.register_blueprint(business_bp, url_prefix='/business')
    app.before_request(load_current_business)

    return app
