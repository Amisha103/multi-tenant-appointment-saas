from app.extensions import db

class Appointment(db.Model):
    __tablename__ = "appointment"

    id = db.Column(db.Integer, primary_key=True)

    time = db.Column(db.DateTime, nullable=False)

    service_id = db.Column(
        db.Integer,
        db.ForeignKey("services.id"),
        nullable=False
    )

    service = db.relationship("Service", backref="appointments")

    staff_id = db.Column(
        db.Integer,
        db.ForeignKey("staff.id"),
        nullable=True
    )

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("businesses.id"),
        nullable=False
    )

    is_booked = db.Column(db.Boolean, default=False)

    customer_name = db.Column(db.String(100))
    customer_email = db.Column(db.String(100))
    __table_args__ = (
    db.UniqueConstraint(
        "tenant_id",
        "staff_id",
        "service_id",
        "time",
        name="unique_slot_per_service_staff_time"
    ),
)