from app.extensions import db
from datetime import datetime

class BusinessUser(db.Model):
    __tablename__ = "business_users"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    business_id = db.Column(db.Integer, db.ForeignKey("businesses.id"), nullable=False)

    role = db.Column(db.String(20), nullable=False)  # admin / staff / customer

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="businesses")
    business = db.relationship("Business", back_populates="users")