from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length, Regexp



from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional

class Etape1Form(FlaskForm):
    # Durée du contrat
    duree_contrat = StringField('Durée du contrat', validators=[DataRequired()])

    # Période et périodicité
    periode_debut = DateField('Date de début', format='%Y-%m-%d', validators=[DataRequired()])
    periode_fin = DateField('Date de fin', format='%Y-%m-%d', validators=[DataRequired()])
    periodicite = SelectField(
        'Périodicité',
        choices=[
            ('annuelle', 'Annuelle')
        ],
        validators=[DataRequired()]
    )

    # Prime
    prime_nette = DecimalField('Prime nette', places=2, validators=[DataRequired(), NumberRange(min=0)])
    accessoires = DecimalField('Accessoires', places=2, validators=[NumberRange(min=0)])
    taxes = DecimalField('Taxes', places=2, validators=[Optional(), NumberRange(min=0)])
    prime_totale = DecimalField('Prime totale', places=2, validators=[Optional()])

    # Risques et capitaux garantis
    deces_accident = DecimalField('Décès accident', places=2, validators=[DataRequired(), NumberRange(min=0)])
    deces_toutes_causes = DecimalField('Décès toutes causes', places=2, validators=[DataRequired(), NumberRange(min=0)])
    invalidite = DecimalField('Invalidité', places=2, validators=[DataRequired(), NumberRange(min=0)])


from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

class Etape2Form(FlaskForm):
    # Assuré
    assure_nom = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    assure_prenoms = StringField('Prénoms', validators=[DataRequired(), Length(max=100)])
    assure_tel = StringField('Téléphone', validators=[DataRequired(), Regexp(r'^\+?\d{8,15}$', message="Numéro de téléphone invalide")])
    assure_date_naissance = DateField('Date de naissance', format='%Y-%m-%d', validators=[DataRequired()])
    assure_adresse = StringField('Adresse', validators=[DataRequired(), Length(max=200)])

    # Bénéficiaire
    beneficiaire_nom = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    beneficiaire_prenoms = StringField('Prénoms', validators=[DataRequired(), Length(max=100)])
    beneficiaire_tel = StringField('Téléphone', validators=[DataRequired(), Regexp(r'^\+?\d{8,15}$', message="Numéro de téléphone invalide")])
    beneficiaire_profession = StringField('Profession', validators=[DataRequired(), Length(max=100)])
    beneficiaire_adresse = StringField('Adresse', validators=[DataRequired(), Length(max=200)])

    # Souscripteur
    souscripteur_nom = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    souscripteur_prenoms = StringField('Prénoms', validators=[DataRequired(), Length(max=100)])
    souscripteur_tel = StringField('Téléphone', validators=[DataRequired(), Regexp(r'^\+?\d{8,15}$', message="Numéro de téléphone invalide")])
    souscripteur_date_naissance = DateField('Date de naissance', format='%Y-%m-%d', validators=[DataRequired()])
    souscripteur_adresse = StringField('Adresse', validators=[DataRequired(), Length(max=200)])

    submit = SubmitField('Suivant')


from flask_wtf import FlaskForm
from wtforms import StringField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class Etape3Form(FlaskForm):
    # Conditions Générales
    ack_conditions = BooleanField('J\'accepte les conditions générales', validators=[DataRequired()])

    # Signature
    lieu_signature = StringField('Lieu de signature', validators=[DataRequired(), Length(max=100)])
    date_signature = DateField('Date de signature', format='%Y-%m-%d', validators=[DataRequired()])

    submit = SubmitField('Valider')




from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional

class QuestionnaireFafa(db.Model):
    __tablename__ = 'questionnaire_fafa'
    
    id = db.Column(db.Integer, primary_key=True)
    duree_contrat = db.Column(db.String(50))
    periode_debut = db.Column(db.Date)
    periode_fin = db.Column(db.Date)
    periodicite = db.Column(db.String(50))
    prime_nette = db.Column(db.Float)
    accessoires = db.Column(db.Float)
    taxes = db.Column(db.Float)
    prime_totale = db.Column(db.Float)
    deces_accident = db.Column(db.Float)
    deces_toutes_causes = db.Column(db.Float)
    invalidite = db.Column(db.Float)
    hospitalisation = db.Column(db.Float)
    traitement_medical = db.Column(db.Float)
    indemnite_journaliere = db.Column(db.Float)
    assure_nom = db.Column(db.String(100))
    assure_prenoms = db.Column(db.String(100))
    assure_tel = db.Column(db.String(20))
    assure_date_naissance = db.Column(db.Date)
    assure_adresse = db.Column(db.String(200))
    beneficiaire_nom = db.Column(db.String(100))
    beneficiaire_prenoms = db.Column(db.String(100))
    beneficiaire_tel = db.Column(db.String(20))
    beneficiaire_adresse = db.Column(db.String(200))
    beneficiaire_profession = db.Column(db.String(100))
    beneficiaire_lateralite = db.Column(db.String(50))
    souscripteur_nom = db.Column(db.String(100))
    souscripteur_prenoms = db.Column(db.String(100))
    souscripteur_tel = db.Column(db.String(20))
    souscripteur_date_naissance = db.Column(db.Date)
    souscripteur_adresse = db.Column(db.String(200))
    ack_conditions = db.Column(db.Boolean)
    lieu_signature = db.Column(db.String(100))
    date_signature = db.Column(db.Date)






class SouscriptionForm(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired(), Length(max=50)])
    prenom = StringField("Prénom", validators=[DataRequired(), Length(max=50)])
    telephone = StringField(
        "Téléphone",
        validators=[
            DataRequired(),
            Regexp(r'^\+?\d{8,15}$', message="Numéro invalide")
        ]
    )
    ville = StringField("Ville", validators=[DataRequired(), Length(max=50)])
    produit = SelectField(
    "Produit",
    choices=[
        ('Option1', 'Option1 (15 000 FCFA/an)'),
        ('Option2', 'Option2 (20 000 FCFA/an)'),
        #('Bronze', 'Bronze'),
        #('Silver', 'Silver')
    ],
    validators=[DataRequired()]
)

    recaptcha = RecaptchaField()













