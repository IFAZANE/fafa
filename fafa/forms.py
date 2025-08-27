from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class SubscriptionForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    prenom = StringField('Prénom', validators=[DataRequired()])
    telephone = StringField('Téléphone', validators=[DataRequired()])
    ville = StringField('Ville', validators=[DataRequired()])
    produit = SelectField('Produit', choices=[('Bronze', 'Bronze'), ('Silver', 'Silver'), ('Gold', 'Gold')])
    submit = SubmitField('Souscrire')
