from app.extensions import db


class MasterService(db.Model):

    __tablename__ = "master_services"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)

    category = db.Column(db.String(120), nullable=False)