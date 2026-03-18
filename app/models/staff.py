from app.extensions import db
class Staff(db.Model):
    __tablename__ = "staff"

    id = db.Column(db.Integer, primary_key=True)

    staff_id = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), nullable=False)

    name = db.Column(db.String(100), nullable=True)   # set later
    password = db.Column(db.String(200), nullable=True)  # set later

    tenant_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'staff_id'),
        db.UniqueConstraint('tenant_id', 'email'),
    )