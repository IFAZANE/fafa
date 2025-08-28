from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Regexp

class SubscriptionForm(FlaskForm):
    nom = StringField("Nom", validators=[
        DataRequired(message="Le nom est requis.")
    ])
    
    prenom = StringField("Prénom", validators=[
        DataRequired(message="Le prénom est requis.")
    ])
    
    telephone = StringField("Téléphone", validators=[
        DataRequired(message="Le numéro de téléphone est requis."),
        Regexp(r'^\d{8,15}$', message="Numéro de téléphone invalide (8 à 15 chiffres attendus).")
    ])
    
    ville = StringField("Ville", validators=[
        DataRequired(message="La ville est requise.")
    ])
    
    produit = SelectField("Produit", choices=[
        ("", "Sélectionnez un produit"),
        ("Option1", "15 000F/ans"),
        ("Option2", "20 000F/ans")
        
    ], validators=[
        DataRequired(message="Veuillez sélectionner un produit.")
    ])
    
    recaptcha = RecaptchaField()
    submit = SubmitField("Souscrire")

