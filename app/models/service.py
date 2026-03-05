from app.extensions import db


class Service(db.Model):

    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)

    business_id = db.Column(
        db.Integer,
        db.ForeignKey("business.id"),
        nullable=False
    )

    master_service_id = db.Column(
        db.Integer,
        db.ForeignKey("master_services.id"),
        nullable=False
    )

    price = db.Column(db.Integer)

    duration = db.Column(db.Integer)

    master_service = db.relationship("MasterService")