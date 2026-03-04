from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_message = "Please login to continue."
login_manager.login_message_category = "warning"

db = SQLAlchemy()
migrate = Migrate()