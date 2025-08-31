from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length, Regexp








from flask_wtf import FlaskForm
from wtforms import (
    StringField, DateField, SubmitField, SelectField, TelField, TextAreaField,
    DecimalField, RadioField, BooleanField
)
from wtforms.validators import DataRequired, Length, Optional, NumberRange, InputRequired

class QuestionnaireForm(FlaskForm):
    # ── Contrat / mentions ──────────────────────────────────────────────────────
    duree_contrat = RadioField(
        "Durée du contrat",
        choices=[
            ("societe", "Durée de la société, résiliation annuelle (préavis ≥ 2 mois)"),
            ("ferme", "Durée ferme d’un an, cessation à la date anniversaire à 24h00"),
        ],
        validators=[DataRequired()]
    )
    periode_debut = DateField("Période du (date de début)", validators=[Optional()])
    periode_fin = DateField("au (date de fin)", validators=[Optional()])
    periodicite = SelectField("Périodicité de paiement de la prime", choices=[("annuelle", "Annuelle")])

    # ── Prime ───────────────────────────────────────────────────────────────────
    prime_nette = DecimalField("Prime nette", places=2, rounding=None, validators=[Optional(), NumberRange(min=0)])
    accessoires = DecimalField("Accessoires", places=2, rounding=None, validators=[Optional(), NumberRange(min=0)])
    taxes = DecimalField("Taxes", places=2, rounding=None, validators=[Optional(), NumberRange(min=0)])
    prime_totale = DecimalField("Prime totale", places=2, rounding=None, validators=[Optional(), NumberRange(min=0)])

    # ── Risques et capitaux garantis ────────────────────────────────────────────
    deces_accident = DecimalField("Décès (à la suite d’accident)", places=2, validators=[Optional(), NumberRange(min=0)])
    deces_toutes_causes = DecimalField("Décès toutes causes", places=2, validators=[Optional(), NumberRange(min=0)])
    invalidite = DecimalField("Invalidité", places=2, validators=[Optional(), NumberRange(min=0)])
    hospitalisation = DecimalField("Hospitalisation", places=2, validators=[Optional(), NumberRange(min=0)])
    traitement_medical = DecimalField("Traitement médical", places=2, validators=[Optional(), NumberRange(min=0)])
    indemnite_journaliere = DecimalField("Indemnité journalière", places=2, validators=[Optional(), NumberRange(min=0)])

    # ── Assuré (si différent du souscripteur) ──────────────────────────────────
    assure_nom = StringField("Nom de l’assuré", validators=[Optional(), Length(max=100)])
    assure_prenoms = StringField("Prénoms de l’assuré", validators=[Optional(), Length(max=100)])
    assure_tel = TelField("Téléphone de l’assuré", validators=[Optional(), Length(max=20)])
    assure_date_naissance = DateField("Date de naissance de l’assuré", validators=[Optional()])
    assure_adresse = TextAreaField("Adresse de l’assuré", validators=[Optional(), Length(max=255)])

    # ── Bénéficiaire ───────────────────────────────────────────────────────────
    beneficiaire_nom = StringField("Nom du bénéficiaire", validators=[Optional(), Length(max=100)])
    beneficiaire_prenoms = StringField("Prénoms du bénéficiaire", validators=[Optional(), Length(max=100)])
    beneficiaire_tel = TelField("Téléphone du bénéficiaire", validators=[Optional(), Length(max=20)])
    beneficiaire_adresse = TextAreaField("Adresse du bénéficiaire", validators=[Optional(), Length(max=255)])
    beneficiaire_profession = StringField("Profession du bénéficiaire", validators=[Optional(), Length(max=100)])
    beneficiaire_lateralite = SelectField("Latéralité", choices=[("droitier", "Droitier"), ("gaucher", "Gaucher")], validators=[Optional()])

    # ── Souscripteur ───────────────────────────────────────────────────────────
    souscripteur_nom = StringField("Nom du souscripteur", validators=[DataRequired(), Length(max=100)])
    souscripteur_prenoms = StringField("Prénoms du souscripteur", validators=[DataRequired(), Length(max=100)])
    souscripteur_tel = TelField("Téléphone du souscripteur", validators=[DataRequired(), Length(max=20)])
    souscripteur_date_naissance = DateField("Date de naissance du souscripteur", validators=[DataRequired()])
    souscripteur_adresse = TextAreaField("Adresse du souscripteur", validators=[Optional(), Length(max=255)])

    # ── Mentions / signatures ──────────────────────────────────────────────────
    ack_conditions = BooleanField(
        "Je reconnais avoir reçu un exemplaire des Conditions Générales",
        validators=[InputRequired(message="Veuillez reconnaître réception des Conditions Générales")]
    )
    lieu_signature = StringField("Fait à", validators=[Optional(), Length(max=100)])
    date_signature = DateField("Le", validators=[Optional()])

    submit = SubmitField("Enregistrer")






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






