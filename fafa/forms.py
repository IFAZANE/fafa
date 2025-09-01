from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length, Regexp







from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional

class QuestionnaireFAFAForm(FlaskForm):
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
    beneficiaire_lateralite = SelectField("Latéralité", choices=[('Droit','Droit'),('Gauche','Gauche')], validators=[Optional()])
    
    souscripteur_nom = StringField("Nom souscripteur", validators=[DataRequired()])
    souscripteur_prenoms = StringField("Prénoms souscripteur", validators=[DataRequired()])
    souscripteur_tel = StringField("Téléphone souscripteur", validators=[DataRequired()])
    souscripteur_date_naissance = DateField("Date de naissance souscripteur", validators=[DataRequired()])
    souscripteur_adresse = StringField("Adresse souscripteur", validators=[Optional()])
    
    ack_conditions = BooleanField("J'accepte les conditions générales", validators=[DataRequired()])
    lieu_signature = StringField("Lieu de signature", validators=[Optional()])
    date_signature = DateField("Date de signature", validators=[Optional()])
    
    submit = SubmitField("Soumettre")






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







