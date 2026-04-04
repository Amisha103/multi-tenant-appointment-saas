from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    email = db.Column(db.String(150), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔗 Mapping relationship (User ↔ BusinessUser)
    business_links = db.relationship(
        "BusinessUser",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # 🔥 Direct access to businesses (very useful)
    businesses = db.relationship(
        "Business",
        secondary="business_users",
        viewonly=True
    )

    # 🔐 Password methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))