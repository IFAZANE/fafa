import os
import uuid
import logging
from flask import Flask, render_template, flash, request
from config import Config
from models import db, Subscription
from forms import SubscriptionForm
from admin import admin_bp
from export import export_csv
from sqlalchemy.exc import IntegrityError

# -----------------------------------------------------------------------------
# App & Config
# -----------------------------------------------------------------------------
app = Flask(__name__)
app.config.from_object(Config)

# Logging (affiche les causes dans les logs Render)
logging.basicConfig(level=logging.INFO)
logger = app.logger

# DB URL: normaliser si Render fournit "postgres://"
_db_url = os.environ.get(
    'DATABASE_URL',
    'postgresql://fafadb_user:yWH0gommUR5p2YCX7Yh4ZqMSG3ww9gEU@dpg-d2njb4ggjchc7386ikhg-a.oregon-postgres.render.com:5432/fafadb'
)
if _db_url.startswith('postgres://'):
    _db_url = _db_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = _db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Sécurité / Captcha
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'changeme')
app.config['RECAPTCHA_PUBLIC_KEY'] = os.environ.get('RECAPTCHA_PUBLIC_KEY', '')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get('RECAPTCHA_PRIVATE_KEY', '')

# Flag: reCAPTCHA présent ?
HAS_RECAPTCHA = bool(
    app.config.get('RECAPTCHA_PUBLIC_KEY') and app.config.get('RECAPTCHA_PRIVATE_KEY')
)

# DB init
db.init_app(app)
with app.app_context():
    db.create_all()

# Blueprints
app.register_blueprint(admin_bp)

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    form = SubscriptionForm()

    # Si pas de clés reCAPTCHA -> enlever le champ pour ne pas casser la validation
    if not HAS_RECAPTCHA and 'recaptcha' in form._fields:
        form._fields.pop('recaptcha', None)

    total = Subscription.query.count()

    if request.method == 'POST':
        logger.info("POST reçu. Errors avant validation: %s", dict(form.errors))
    if form.validate_on_submit():
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
            flash("Souscription réussie !", "success")

            # ✅ Affichage direct de confirmation.html (pas de redirection)
            return render_template('confirmation.html', uuid=sub.uuid)

        except IntegrityError as ie:
            db.session.rollback()
            logger.exception("Contrainte d'unicité (ex: téléphone déjà pris) : %s", ie)
            flash("Cette souscription existe déjà (ex: téléphone déjà utilisé).", "danger")
        except Exception as e:
            db.session.rollback()
            logger.exception("Erreur lors de la souscription : %s", e)
            flash("Erreur lors de la souscription. Veuillez réessayer.", "danger")
    else:
        # En cas d'échec de validation, remonter clairement les erreurs
        if request.method == 'POST':
            logger.info("Validation échouée: %s", dict(form.errors))
            flash("Veuillez corriger les erreurs du formulaire.", "danger")

    return render_template('index.html', form=form, total=total, has_recaptcha=HAS_RECAPTCHA)

# Export CSV
app.add_url_rule('/export', 'export_csv', export_csv)

@app.route('/manuel')
def manuel():
    return render_template('manuel.html')

# Dev
if __name__ == '__main__':
    app.run(debug=True)
