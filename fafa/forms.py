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

class QuestionnaireForm(FlaskForm):
    periode_debut = DateField("Pour la période du", validators=[DataRequired()])
    periode_fin = DateField("au", validators=[DataRequired()])
    periodicite = SelectField("Périodicité", choices=[('Mensuelle','Mensuelle'),('Annuel','Annuel')], validators=[DataRequired()])
    
    prime_nette = FloatField("Prime nette", validators=[DataRequired()])
    accessoires = FloatField("Accessoires", validators=[DataRequired()])
    taxes = FloatField("Taxes", validators=[DataRequired()])
    prime_totale = FloatField("Prime totale", validators=[DataRequired()])
    
    deces_accident = FloatField("Décès accident", validators=[Optional()])
    deces_toutes_causes = FloatField("Décès toutes causes", validators=[Optional()])
    invalidite = FloatField("Invalidité", validators=[Optional()])
    hospitalisation = FloatField("Hospitalisation", validators=[Optional()])
    traitement_medical = FloatField("Traitement médical", validators=[Optional()])
    indemnite_journaliere = FloatField("Indemnité journalière", validators=[Optional()])
    
    assure_nom = StringField("Nom", validators=[Optional()])
    assure_prenoms = StringField("Prénoms", validators=[Optional()])
    assure_tel = StringField("Téléphone", validators=[Optional()])
    assure_date_naissance = DateField("Date de naissance", validators=[Optional()])
    assure_adresse = StringField("Adresse", validators=[Optional()])
    
    beneficiaire_nom = StringField("Nom bénéficiaire", validators=[Optional()])
    beneficiaire_prenoms = StringField("Prénoms bénéficiaire", validators=[Optional()])
    beneficiaire_tel = StringField("Téléphone bénéficiaire", validators=[Optional()])
    beneficiaire_profession = StringField("Profession bénéficiaire", validators=[Optional()])
    beneficiaire_adresse = StringField("Adresse bénéficiaire", validators=[Optional()])
    #beneficiaire_lateralite = SelectField("Latéralité", choices=[('Droit','Droit'),('Gauche','Gauche')], validators=[Optional()])
    
    souscripteur_nom = StringField("Nom souscripteur", validators=[DataRequired()])
    souscripteur_prenoms = StringField("Prénoms souscripteur", validators=[DataRequired()])
    souscripteur_tel = StringField("Téléphone souscripteur", validators=[DataRequired()])
    souscripteur_date_naissance = DateField("Date de naissance souscripteur", validators=[DataRequired()])
    souscripteur_adresse = StringField("Adresse souscripteur", validators=[Optional()])
    
    ack_conditions = BooleanField("J'accepte les conditions générales", validators=[DataRequired()])
    lieu_signature = StringField("Lieu de signature", validators=[Optional()])
    date_signature = DateField("Date de signature", validators=[Optional()])
    
    submit = SubmitField("Soumettre")



from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional







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













