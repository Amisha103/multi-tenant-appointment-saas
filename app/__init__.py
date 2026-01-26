from flask import Flask
from app.config import Config
from app.extensions import db, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.health import health_bp
    app.register_blueprint(health_bp)

    return app
