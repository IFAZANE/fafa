from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class SouscriptionForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    prenom = StringField('Prénom', validators=[DataRequired()])
    telephone = StringField('Téléphone', validators=[DataRequired()])
    ville = StringField('Ville', validators=[DataRequired()])
    
    # On ne propose que Option1 et Option2
    produit = SelectField(
        'Produit',
        choices=[('Option1', 'Option1 (15 000 F/ans)'), ('Option2', 'Option2 (20 000 F/ans)')],
        validators=[DataRequired()]
    )
    
    submit = SubmitField('Souscrire')
