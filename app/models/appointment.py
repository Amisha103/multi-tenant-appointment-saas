
from app.extensions import db
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(db.String(100))
    service = db.Column(db.String(100))

    date = db.Column(db.Date)
    time = db.Column(db.Time)

    status = db.Column(db.String(20), default="pending")

    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"))
    tenant_id = db.Column(db.Integer)