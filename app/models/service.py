from app.extensions import db


class Service(db.Model):

    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("businesses.id"),
        nullable=False
    )

    master_service_id = db.Column(
        db.Integer,
        db.ForeignKey("master_services.id"),
        nullable=False
    )

    price = db.Column(db.Integer)

    duration = db.Column(db.Integer)

    business = db.relationship(
        "Business",
        back_populates="services"
    )