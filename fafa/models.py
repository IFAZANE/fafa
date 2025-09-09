import uuid
import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, validators, BooleanField

from wtforms.validators import DataRequired
from wtforms.validators import DataRequired, Regexp



db = SQLAlchemy()


from flask_sqlalchemy import SQLAlchemy
from datetime import date
from datetime import datetime

db = SQLAlchemy()



class QuestionnaireFafa(db.Model):
    __tablename__ = 'questionnaire_fafa'

    id = db.Column(db.Integer, primary_key=True)
    type_contrat = db.Column(db.Integer, nullable=False)  # 15000 ou 20000
    assure_nom = db.Column(db.String(100))
    assure_prenoms = db.Column(db.String(100))
    assure_tel = db.Column(db.String(20))
    assure_date_naissance = db.Column(db.Date)
    assure_adresse = db.Column(db.String(200))
    souscripteur_nom = db.Column(db.String(100))
    souscripteur_prenoms = db.Column(db.String(100))
    souscripteur_tel = db.Column(db.String(20))
    souscripteur_date_naissance = db.Column(db.Date)
    souscripteur_adresse = db.Column(db.String(200))
    ack_conditions = db.Column(db.Boolean)
    lieu_signature = db.Column(db.String(100))
    date_signature = db.Column(db.Date)
    
    profession = db.Column(db.String(100), nullable=False)
    est_droitier = db.Column(db.Boolean)
    est_gaucher = db.Column(db.Boolean)

    beneficiaire_nom = db.Column(db.String(100), nullable=False)
    beneficiaire_prenoms = db.Column(db.String(100), nullable=False)
    beneficiaire_tel = db.Column(db.String(20), nullable=False)
    beneficiaire_mail = db.Column(db.String(120), nullable=False)
    beneficiaire_adresse = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



#class Paiement(db.Model):
#   __tablename__ = 'paiements'

#    id = db.Column(db.Integer, primary_key=True)
#    questionnaire_fafa_id = db.Column(db.Integer, db.ForeignKey('questionnaire_fafa.id'), nullable=False)
#    transaction_id = db.Column(db.String(255), unique=True, nullable=False)
#    amount = db.Column(db.Numeric, nullable=False)
#    currency = db.Column(db.String(3), default='XOF')
#    payment_method = db.Column(db.String(50), default='mobilemoney')
#    phone = db.Column(db.String(20))
#    status = db.Column(db.String(20), default='pending')
#    response = db.Column(db.JSON)
#    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
#    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

#    questionnaire_fafa = db.relationship('QuestionnaireFafa', backref=db.backref('paiements', lazy=True))

from sqlalchemy.dialects.postgresql import JSON

class Paiement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questionnaire_fafa_id = db.Column(db.Integer, db.ForeignKey('questionnaire_fafa.id'))
    transaction_id = db.Column(db.String(64), unique=True, nullable=False)
    amount = db.Column(db.Integer)
    currency = db.Column(db.String(8))
    phone = db.Column(db.String(20))
    status = db.Column(db.String(32))
    response = db.Column(JSON)  # ou db.Text si tu fais json.dumps()
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    
#class QuestionnaireFafa(db.Model):
#    __tablename__ = 'questionnaire_fafa'

#    id = db.Column(db.Integer, primary_key=True)

    # Contrat / période
#    duree_contrat = db.Column(db.String(10), nullable=False)
#    periode_debut = db.Column(db.Date)
#    periode_fin = db.Column(db.Date)
#    periodicite = db.Column(db.String(20))

    # Prime
#    prime_nette = db.Column(db.Numeric(12, 2))
#    accessoires = db.Column(db.Numeric(12, 2))
#    taxes = db.Column(db.Numeric(12, 2))
#    prime_totale = db.Column(db.Numeric(12, 2))

    # Risques et capitaux garantis
#    deces_accident = db.Column(db.Numeric(14, 2))
#    deces_toutes_causes = db.Column(db.Numeric(14, 2))
#    invalidite = db.Column(db.Numeric(14, 2))
#    hospitalisation = db.Column(db.Numeric(14, 2))
#    traitement_medical = db.Column(db.Numeric(14, 2))
#    indemnite_journaliere = db.Column(db.Numeric(14, 2))

    # Assuré
#    assure_nom = db.Column(db.String(100))
#    assure_prenoms = db.Column(db.String(100))
#    assure_tel = db.Column(db.String(20))
#    assure_date_naissance = db.Column(db.Date)
#    assure_adresse = db.Column(db.String(255))

    # Bénéficiaire
#    beneficiaire_nom = db.Column(db.String(100))
#    beneficiaire_prenoms = db.Column(db.String(100))
#    beneficiaire_tel = db.Column(db.String(20))
#    beneficiaire_adresse = db.Column(db.String(255))
#    beneficiaire_profession = db.Column(db.String(100))
#    beneficiaire_lateralite = db.Column(db.String(10))

    # Souscripteur
#    souscripteur_nom = db.Column(db.String(100), nullable=True)
#    souscripteur_prenoms = db.Column(db.String(100), nullable=True)
#    souscripteur_tel = db.Column(db.String(20), nullable=True)
#    souscripteur_date_naissance = db.Column(db.Date, nullable=True)
#    souscripteur_adresse = db.Column(db.String(255))

    # Mentions finales
#    ack_conditions = db.Column(db.Boolean, nullable=False, default=False)
#    lieu_signature = db.Column(db.String(100))
#    date_signature = db.Column(db.Date)



class Subscription(db.Model):
    __tablename__ = 'subscription'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True)
    nom = db.Column(db.String(50))
    prenom = db.Column(db.String(50))
    telephone = db.Column(db.String(15), unique=True)
    ville = db.Column(db.String(50))
    produit = db.Column(db.String(50), nullable=False)























