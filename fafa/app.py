from flask import Flask, render_template, redirect, flash, url_for
from config import Config
from models import db, Subscription
from forms import SubscriptionForm
from admin import admin_bp
from export import export_csv
import os
import uuid

# 1️⃣ Créer l'application Flask
app = Flask(__name__)
app.config.from_object(Config)

# 2️⃣ Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://fafadb_user:yWH0gommUR5p2YCX7Yh4ZqMSG3ww9gEU@dpg-d2njb4ggjchc7386ikhg-a.oregon-postgres.render.com:5432/fafadb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3️⃣ Configuration sécurité / CAPTCHA
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'changeme')
app.config['RECAPTCHA_PUBLIC_KEY'] = os.environ.get('RECAPTCHA_PUBLIC_KEY', '')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get('RECAPTCHA_PRIVATE_KEY', '')

# 4️⃣ Initialiser la base de données
db.init_app(app)
with app.app_context():
    db.create_all()

# 5️⃣ Enregistrer les blueprints (ex : admin)
app.register_blueprint(admin_bp)

# 6️⃣ Route principale : page d'inscription
@app.route('/', methods=['GET', 'POST'])
def index():
    form = SubscriptionForm()
    total = Subscription.query.count()

    if form.validate_on_submit():
        try:
            sub = Subscription(
                #uuid=str(uuid.uuid4()),
                nom=form.nom.data,
                prenom=form.prenom.data,
                telephone=form.telephone.data,
                ville=form.ville.data,
                produit=form.produit.data
            )
            db.session.add(sub)
            db.session.commit()
            flash("Souscription réussie !", "success")
            #return render_template('confirmation.html', uuid=sub.uuid)
            return render_template('confirmation.html', code=sub.code)
        except Exception as e:
            db.session.rollback()
            flash("Erreur lors de la souscription. Veuillez réessayer.", "danger")

    return render_template('index.html', form=form, total=total)

@app.route('/confirmation/<int:subscription_id>')
def confirmation(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    return render_template('confirmation.html', code=subscription.code)

# 7️⃣ Route d'export CSV
app.add_url_rule('/export', 'export_csv', export_csv)

@app.route('/manuel')
def manuel():
    return render_template('manuel.html')


# 8️⃣ Exécution de l'application en local
if __name__ == '__main__':
    app.run(debug=True)


