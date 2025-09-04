from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length, Regexp

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, BooleanField, RadioField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Regexp, Email



from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional

class Etape1Form(FlaskForm):
    # Souscripteur
    souscripteur_nom = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    souscripteur_prenoms = StringField('Prénoms', validators=[DataRequired(), Length(max=100)])
    souscripteur_tel = StringField('Téléphone', validators=[DataRequired(), Regexp(r'^\+?\d{8,15}$', message="Numéro de téléphone invalide")])
    souscripteur_date_naissance = DateField('Date de naissance', format='%Y-%m-%d', validators=[DataRequired()])
    souscripteur_adresse = StringField('Adresse', validators=[DataRequired(), Length(max=200)])
    # Assuré
    assure_nom = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    assure_prenoms = StringField('Prénoms', validators=[DataRequired(), Length(max=100)])
    assure_tel = StringField('Téléphone', validators=[DataRequired(), Regexp(r'^\+?\d{8,15}$', message="Numéro de téléphone invalide")])
    assure_date_naissance = DateField('Date de naissance', format='%Y-%m-%d', validators=[DataRequired()])
    assure_adresse = StringField('Adresse', validators=[DataRequired(), Length(max=200)])

    # Durée du contrat
#    duree_contrat = StringField('Durée du contrat', validators=[DataRequired()])

    # Période et périodicité
 #   periode_debut = DateField('Date de début', format='%Y-%m-%d', validators=[DataRequired()])
 #   periode_fin = DateField('Date de fin', format='%Y-%m-%d', validators=[DataRequired()])
 #   periodicite = SelectField(
 #       'Périodicité',
 #      choices=[
 #           ('annuelle', 'Annuelle')
 #       ],
 #       validators=[DataRequired()]
 #   )

    # Prime
 #   type_contrat = SelectField(
 #   "Type de contrat",
 #   choices=[
 #       ("15000", "15 000 FCFA / an"),
 #       ("20000", "20 000 FCFA / an")
 #   ],
 #   validators=[DataRequired()]
#)

    ## Risques et capitaux garantis
    #deces_accident = DecimalField('Décès accident', places=2, validators=[DataRequired(), NumberRange(min=0)])
    #deces_toutes_causes = DecimalField('Décès toutes causes', places=2, validators=[DataRequired(), NumberRange(min=0)])
    #invalidite = DecimalField('Invalidité', places=2, validators=[DataRequired(), NumberRange(min=0)])


from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, RadioField, EmailField
from wtforms.validators import DataRequired, Length, Regexp, Email

class Etape2Form(FlaskForm):
    # Étape 2 — Déclarations
    profession = StringField('Profession', validators=[DataRequired(), Length(max=100)])
    est_droitier = BooleanField('Droitier')
    est_gaucher = BooleanField('Gaucher')

    # Bénéficiaire
    beneficiaire_nom = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    beneficiaire_prenoms = StringField('Prénoms', validators=[DataRequired(), Length(max=100)])
    beneficiaire_tel = StringField('Téléphone', validators=[DataRequired(), Regexp(r'^\+?\d{8,15}$')])
    beneficiaire_mail = EmailField('Mail', validators=[DataRequired(), Email()])
    beneficiaire_adresse = StringField('Adresse', validators=[DataRequired(), Length(max=200)])

    conditions_acceptees = BooleanField("J'accepte les conditions", validators=[DataRequired(message="Vous devez accepter les conditions")])

    # Étape 3 — Choix de l'option FAFA
    choix_fafa = RadioField('Option FAFA', choices=[
        ('15000', 'FAFA 1 (15 000 FCFA)'),
        ('20000', 'FAFA 2 (20 000 FCFA)')
    ], validators=[DataRequired()])



#from flask_wtf import FlaskForm
#from wtforms import StringField, DateField, BooleanField, SubmitField
#from wtforms.validators import DataRequired, Length

#class Etape3Form(FlaskForm):
#    # Conditions Générales
#    ack_conditions = BooleanField('J\'ai lu et j\'accepte les conditions générales', validators=[DataRequired()])

#    # Signature
#    lieu_signature = StringField('Lieu de signature', validators=[DataRequired(), Length(max=100)])
#    date_signature = DateField('Date de signature', format='%Y-%m-%d', validators=[DataRequired()])

#    submit = SubmitField('Valider')






from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, BooleanField, RadioField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Regexp, Email

class QuestionnaireFafaForm(FlaskForm):
    type_contrat = RadioField('Option FAFA', choices=[
        ('15000', 'FAFA 1 (15 000 FCFA)'),
        ('20000', 'FAFA 2 (20 000 FCFA)')
    ], validators=[DataRequired()])
    
    assure_nom = StringField('Nom de l\'assuré', validators=[DataRequired()])
    assure_prenoms = StringField('Prénoms de l\'assuré', validators=[DataRequired()])
    assure_tel = StringField('Téléphone de l\'assuré', validators=[
        DataRequired(),
        Regexp(r'^\+?\d{8,15}$', message="Numéro de téléphone invalide")
    ])
    assure_date_naissance = DateField('Date de naissance', validators=[DataRequired()])
    assure_adresse = StringField('Adresse', validators=[DataRequired()])
    
    souscripteur_nom = StringField('Nom du souscripteur', validators=[DataRequired()])
    souscripteur_prenoms = StringField('Prénoms du souscripteur', validators=[DataRequired()])
    souscripteur_tel = StringField('Téléphone du souscripteur', validators=[
        DataRequired(),
        Regexp(r'^\+?\d{8,15}$', message="Numéro de téléphone invalide")
    ])
    souscripteur_date_naissance = DateField('Date de naissance du souscripteur', validators=[DataRequired()])
    souscripteur_adresse = StringField('Adresse du souscripteur', validators=[DataRequired()])
    
    profession = StringField('Profession', validators=[DataRequired()])
    est_droitier = BooleanField('Droitier')
    est_gaucher = BooleanField('Gaucher')

    beneficiaire_nom = StringField('Nom du bénéficiaire', validators=[DataRequired()])
    beneficiaire_prenoms = StringField('Prénoms du bénéficiaire', validators=[DataRequired()])
    beneficiaire_tel = StringField('Téléphone du bénéficiaire', validators=[
        DataRequired(),
        Regexp(r'^\+?\d{8,15}$', message="Numéro de téléphone invalide")
    ])
    beneficiaire_mail = EmailField('Email du bénéficiaire', validators=[DataRequired(), Email()])
    beneficiaire_adresse = StringField('Adresse du bénéficiaire', validators=[DataRequired()])

    ack_conditions = BooleanField("J'accepte les conditions", validators=[DataRequired()])
    lieu_signature = StringField('Lieu de signature', validators=[DataRequired()])
    date_signature = DateField('Date de signature', validators=[DataRequired()])

    
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

























