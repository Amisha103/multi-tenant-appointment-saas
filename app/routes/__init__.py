from app.routes.landing_routes import landing_bp
from app.routes.business_routes import business_bp


def register_routes(app):
    app.register_blueprint(landing_bp)
    app.register_blueprint(business_bp, url_prefix="/business")

