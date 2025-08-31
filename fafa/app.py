from flask import Flask, render_template, redirect, flash, url_for, Response
from config import Config
from models import db, Subscription
from forms import SouscriptionForm
from admin import admin_bp
import os
import uuid
import csv
from io import StringIO, BytesIO
from openpyxl import Workbook

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

# 5️⃣ Enregistrer les blueprints
app.register_blueprint(admin_bp)


@app.route("/questionnaire", methods=["GET", "POST"])
def questionnaire():
    form = QuestionnaireForm()
    if form.validate_on_submit():
        # TODO: insérer en base (SQLAlchemy ou SQL brut)
        flash("Souscription enregistrée", "success")
        return redirect(url_for("questionnaire"))
    return render_template("questionnaire.html", form=form)


# 6️⃣ Route principale : page d'inscription
@app.route('/')
def accueil():
    return render_template('home.html')
    
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = SouscriptionForm()
    total = Subscription.query.count()

    if form.validate_on_submit():
        # Vérifier doublons
        existing = Subscription.query.filter_by(telephone=form.telephone.data).first()
        if existing:
            flash("Ce numéro est déjà enregistré.", "danger")
        else:
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
                return redirect(url_for('confirmation', uuid=sub.uuid))
            except Exception as e:
                db.session.rollback()
                flash(f"Erreur lors de la souscription: {str(e)}", "danger")

    return render_template('index.html', form=form, total=total)

# 7️⃣ Page de confirmation
@app.route('/confirmation/<uuid>')
def confirmation(uuid):
    sub = Subscription.query.filter_by(uuid=uuid).first_or_404()
    return render_template('confirmation.html', subscription=sub)

# 8️⃣ Export CSV
from export import export_csv, export_excel

@app.route('/export/csv')
def route_export_csv():
    return export_csv()

@app.route('/export/excel')
def route_export_excel():
    return export_excel()


# 1️⃣0️⃣ Page manuel
@app.route('/manuel')
def manuel():
    return render_template('manuel.html')

# 1️⃣1️⃣ Debug form (optionnel)
@app.route('/debug_form', methods=['POST'])
def debug_form():
    form = SouscriptionForm()
    if form.validate_on_submit():
        return "Formulaire valide!"
    else:
        return f"Erreurs : {form.errors}"

# 1️⃣2️⃣ Exécution de l'application
if __name__ == '__main__':
    app.run(debug=True)








