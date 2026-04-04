from app.extensions import db
from datetime import datetime


class BusinessUser(db.Model):
    __tablename__ = "business_users"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    business_id = db.Column(db.Integer, db.ForeignKey("businesses.id"), nullable=False)

    role = db.Column(db.String(20), nullable=False, default="admin")  # admin / staff / customer

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🚫 Prevent duplicate user-business entries
    __table_args__ = (
        db.UniqueConstraint('user_id', 'business_id', name='unique_user_business'),
    )

    # 🔗 Relationships
    user = db.relationship("User", back_populates="business_links")
    business = db.relationship("Business", back_populates="users")