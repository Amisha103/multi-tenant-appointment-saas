from app.routes.landing_routes import landing_bp

def register_routes(app):
    app.register_blueprint(landing_bp)