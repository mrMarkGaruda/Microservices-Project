from flask import Flask
from .database import db, migrate
from .blueprints.nutrition import nutrition_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nutrition.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate.init_app(app, db)

app.register_blueprint(nutrition_bp, url_prefix="/nutrition")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
