from app.extensions import db

class Appointment(db.Model):
    __tablename__ = "appointment"

    id = db.Column(db.Integer, primary_key=True)

    time = db.Column(db.DateTime, nullable=False)

    service_id = db.Column(
        db.Integer,
        db.ForeignKey("service.id"),
        nullable=False
    )

    staff_id = db.Column(
        db.Integer,
        db.ForeignKey("staff.id"),
        nullable=True
    )

    # ✅ THIS IS YOUR BUSINESS LINK
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("business.id"),
        nullable=False
    )

    is_booked = db.Column(db.Boolean, default=False)

    customer_name = db.Column(db.String(100))
    customer_email = db.Column(db.String(100))