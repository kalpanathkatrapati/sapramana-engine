from flask import Flask

def create_app():
    app = Flask(__name__)

    # Register routes
    from .views import bp as main_bp
    app.register_blueprint(main_bp)

    return app

# For direct imports
from .views import last_data
