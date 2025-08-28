from flask import Flask, render_template, redirect, flash, url_for
from config import Config
from models import db, Subscription
from forms import SouscriptionForm
from admin import admin_bp
from export import export_csv
import os
import uuid

app = Flask(__name__)
app.config.from_object(Config)

# DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://fafadb_user:motdepasse@serveur:5432/fafadb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Security / CAPTCHA
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'changeme')
app.config['RECAPTCHA_PUBLIC_KEY'] = os.environ.get('RECAPTCHA_PUBLIC_KEY', '')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get('RECAPTCHA_PRIVATE_KEY', '')

# Init DB
db.init_app(app)
with app.app_context():
    db.create_all()

# Blueprints
app.register_blueprint(admin_bp)

# Route principale
@app.route('/', methods=['GET', 'POST'])
def index():
    form = SouscriptionForm()
    total = Subscription.query.count()

    if form.validate_on_submit():
        # Vérification doublon
        existing = Subscription.query.filter_by(telephone=form.telephone.data).first()
        if existing:
            flash("Ce numéro de téléphone est déjà enregistré.", "danger")
            return render_template('index.html', form=form, total=total)

        try:
            sub = Subscription(
                uuid=str(uuid.uuid4()),
                nom=form.nom.data,
                prenom=form.prenom.data,
                telephone=form.telephone.data,
                ville=form.ville.data,
                produit=form.produit.data
            )
            db.session.add(sub)
            db.session.commit()
            return redirect(url_for('confirmation', uuid=sub.uuid))
        except Exception:
            db.session.rollback()
            flash("Erreur lors de la souscription. Veuillez réessayer.", "danger")

    return render_template('index.html', form=form, total=total)


@app.route('/confirmation/<uuid>')
def confirmation(uuid):
    subscription = Subscription.query.filter_by(uuid=uuid).first_or_404()
    return render_template('confirmation.html', uuid=subscription.uuid)


# Export CSV
app.add_url_rule('/export', 'export_csv', export_csv)


@app.route('/manuel')
def manuel():
    return render_template('manuel.html')


if __name__ == '__main__':
    app.run(debug=True)
