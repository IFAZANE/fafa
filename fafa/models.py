import uuid
import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

db = SQLAlchemy()


from sqlalchemy.dialects.postgresql import ENUM

produit_enum = ENUM(
    'Option1', 'Option2', 'Bronze', 'Silver','Gold',   # ajouter Bronze et Silver
    name='produit_enum',
    create_type=False  # ne recrée pas le type si déjà existant
)

class Subscription(db.Model):
    __tablename__ = 'subscription'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True)
    nom = db.Column(db.String(50))
    prenom = db.Column(db.String(50))
    telephone = db.Column(db.String(15), unique=True)
    ville = db.Column(db.String(50))
    produit = db.Column(produit_enum)




