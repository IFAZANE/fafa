from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length, Regexp

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





