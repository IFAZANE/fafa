from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Regexp

class SubscriptionForm(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired()])
    prenom = StringField("Prénom", validators=[DataRequired()])
    telephone = StringField("Téléphone", validators=[
        DataRequired(),
        Regexp(r'^\d{8,15}$', message="Numéro de téléphone invalide")
    ])
    ville = StringField("Ville", validators=[DataRequired()])
    
    produit = SelectField("Produit", choices=[
        ("Bronze", "Bronze"),
        ("Silver", "Silver"),
        ("Gold", "Gold")
    ], validators=[DataRequired()])

    recaptcha = RecaptchaField()
    submit = SubmitField("Souscrire")

