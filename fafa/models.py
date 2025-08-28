#import uuid
#from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import Enum

#db = SQLAlchemy()

#class Subscription(db.Model):
#    id = db.Column(db.Integer, primary_key=True)  # auto-incrément
#    uuid = db.Column(db.String(36), unique=True, nullable=False)
#    nom = db.Column(db.String(50), nullable=False)
#    prenom = db.Column(db.String(50), nullable=False)
#    telephone = db.Column(db.String(20), nullable=False)
#    ville = db.Column(db.String(50), nullable=False)
#    produit = db.Column(Enum('Gold', 'Silver', 'Bronze', name='produit_enum'), nullable=False)



import random
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def generate_unique_code():
    """Génère un code unique à 6 chiffres."""
    while True:
        code = str(random.randint(100000, 999999))
        if not Subscription.query.filter_by(code=code).first():
            return code

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(6), unique=True, default=generate_unique_code)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    ville = db.Column(db.String(50), nullable=False)
    produit = db.Column(db.String(20), nullable=False)




