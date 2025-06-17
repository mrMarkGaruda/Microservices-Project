import logging
from flask import Flask, jsonify
from database import init_db, db_session
from blueprints.billing_blueprint import billing_bp
from services.billing_service import seed_initial_plans
import os
import sys

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    with app.app_context():
        init_db()
        seed_initial_plans()
    app.register_blueprint(billing_bp)
    @app.route("/health")
    def health():
        logger.debug("Billing service health check endpoint called")
        return jsonify({"status": "UP", "service": "Billing Service"})
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()
        logger.debug("Billing DB session removed.")
    return app

app = create_app()

def run_flask_app():
    port = int(os.getenv("BILLING_SERVICE_PORT", 5003))
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    logger.info(f"Starting Billing Service on port {port} with debug mode: {debug_mode}")
    app.run(host="0.0.0.0", port=port, debug=debug_mode, use_reloader=not debug_mode)

if __name__ == "__main__":
    run_flask_app()
