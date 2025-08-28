from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Regexp

class SubscriptionForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    prenom = StringField('Prénom', validators=[DataRequired()])
    telephone = StringField('Téléphone', validators=[DataRequired()])
    ville = StringField('Ville', validators=[DataRequired()])
    produit = SelectField('Produit', choices=[('Bronze', 'Bronze'), ('Silver', 'Silver'), ('Gold', 'Gold')])
    submit = SubmitField('Souscrire')

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SouscriptionForm(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired()])
    prenom = StringField("Prénom", validators=[DataRequired()])
    recaptcha = RecaptchaField()  # <-- captcha
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


