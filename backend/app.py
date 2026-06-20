import logging
import os

from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS
from core.database import init_db
from api.auth import auth_bp
from api.data import data_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(auth_bp)
    app.register_blueprint(data_bp)

    with app.app_context():
        init_db()

    logger.info("TeraCyte proxy backend ready")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
