import uuid
import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

db = SQLAlchemy()


from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class QuestionnaireFafa(db.Model):
    __tablename__ = 'questionnaire_fafa'

    id = db.Column(db.Integer, primary_key=True)

    # Contrat / période
    duree_contrat = db.Column(db.String(10), nullable=False)
    periode_debut = db.Column(db.Date)
    periode_fin = db.Column(db.Date)
    periodicite = db.Column(db.String(20))

    # Prime
    prime_nette = db.Column(db.Numeric(12, 2))
    accessoires = db.Column(db.Numeric(12, 2))
    taxes = db.Column(db.Numeric(12, 2))
    prime_totale = db.Column(db.Numeric(12, 2))

    # Risques et capitaux garantis
    deces_accident = db.Column(db.Numeric(14, 2))
    deces_toutes_causes = db.Column(db.Numeric(14, 2))
    invalidite = db.Column(db.Numeric(14, 2))
    hospitalisation = db.Column(db.Numeric(14, 2))
    traitement_medical = db.Column(db.Numeric(14, 2))
    indemnite_journaliere = db.Column(db.Numeric(14, 2))

    # Assuré
    assure_nom = db.Column(db.String(100))
    assure_prenoms = db.Column(db.String(100))
    assure_tel = db.Column(db.String(20))
    assure_date_naissance = db.Column(db.Date)
    assure_adresse = db.Column(db.String(255))

    # Bénéficiaire
    beneficiaire_nom = db.Column(db.String(100))
    beneficiaire_prenoms = db.Column(db.String(100))
    beneficiaire_tel = db.Column(db.String(20))
    beneficiaire_adresse = db.Column(db.String(255))
    beneficiaire_profession = db.Column(db.String(100))
    beneficiaire_lateralite = db.Column(db.String(10))

    # Souscripteur
    souscripteur_nom = db.Column(db.String(100), nullable=True)
    souscripteur_prenoms = db.Column(db.String(100), nullable=True)
    souscripteur_tel = db.Column(db.String(20), nullable=True)
    souscripteur_date_naissance = db.Column(db.Date, nullable=True)
    souscripteur_adresse = db.Column(db.String(255))

    # Mentions finales
    ack_conditions = db.Column(db.Boolean, nullable=False, default=False)
    lieu_signature = db.Column(db.String(100))
    date_signature = db.Column(db.Date)



class Subscription(db.Model):
    __tablename__ = 'subscription'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True)
    nom = db.Column(db.String(50))
    prenom = db.Column(db.String(50))
    telephone = db.Column(db.String(15), unique=True)
    ville = db.Column(db.String(50))
    produit = db.Column(db.String(50), nullable=False)








