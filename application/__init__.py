import os
from application import navbar
from flask import Flask, make_response, render_template
from dotenv import load_dotenv

nav, search = navbar.create_navbar()

def not_found_error(error):
    return make_response(
        render_template('error.html', navbar=nav, searchbar=search, error=404), 
        404
      )

def internal_error(error):
    return make_response(
        render_template('error.html', navbar=nav, searchbar=search, error=500),
        500
      )

def create_app():
    app = Flask(__name__, template_folder="templates")
    
    if app.config["ENV"] == "production":
        app.config.from_object("config.ProductionConfig")
    else:
        app.config.from_object("config.DevelopmentConfig")

    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_error)

    with app.app_context():
        # Include our Routes
        from .home import routes
        from .analytics import analytics

        # Register Blueprints
        app.register_blueprint(routes.routes_bp)
        app.register_blueprint(analytics.analytics_bp)

        app.secret_key = os.getenv("SESSIONSECRET")

        return app