from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )


    auth_provider = db.Column(
    db.String(20),
    default="local"
)

    profile_picture = db.Column(
    db.String(500),
    nullable=True
)

    email_verified = db.Column(
    db.Boolean,
    default=False
)

    password_hash = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

 
    business_links = db.relationship(
        "BusinessUser",
        back_populates="user",
        cascade="all, delete-orphan"
    )


    businesses = db.relationship(
        "Business",
        secondary="business_users",
        viewonly=True
    )


  
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))