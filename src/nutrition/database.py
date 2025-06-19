# Import SQLAlchemy for ORM database management
from flask_sqlalchemy import SQLAlchemy
# Import Migrate for database migrations
from flask_migrate import Migrate

# Create a SQLAlchemy database instance
db = SQLAlchemy()
# Create a Migrate instance for handling migrations
migrate = Migrate()
