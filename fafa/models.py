from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    ville = db.Column(db.String(50), nullable=False)
    produit = db.Column(db.String(20), nullable=False)
