import os
from flask import Flask
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__, template_folder="templates")
    
    if app.config["ENV"] == "production":
        app.config.from_object("config.ProductionConfig")
    else:
        app.config.from_object("config.DevelopmentConfig")

    with app.app_context():
        # Include our Routes
        from .home import routes
        from .analytics import analytics

        # Register Blueprints
        app.register_blueprint(routes.routes_bp)
        app.register_blueprint(analytics.analytics_bp)
        app.secret_key = os.getenv("SESSIONSECRET")

        return app