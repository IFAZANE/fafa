from flask import (
    Flask, render_template, request, session, send_file, redirect,
    flash, url_for, Response, make_response
)
from config import Config
from models import db, Subscription, QuestionnaireFafa
from forms import (
    SouscriptionForm, Etape1Form, Etape2Form, Etape3Form,
    QuestionnaireForm
)
from admin import admin_bp
from export import export_csv, export_excel
import requests
import uuid
import os
import io
from io import BytesIO
from datetime import datetime, date
from openpyxl import Workbook
from weasyprint import HTML
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# -----------------------------
# 1️⃣ Création de l'application
# -----------------------------
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.environ.get('SECRET_KEY', 'changeme')

# -----------------------------
# 2️⃣ Configuration base de données
# -----------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://fafadb_user:yWH0gommUR5p2YCX7Yh4ZqMSG3ww9gEU@dpg-d2njb4ggjchc7386ikhg-a.oregon-postgres.render.com:5432/fafadb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

# -----------------------------
# 3️⃣ Blueprints
# -----------------------------
app.register_blueprint(admin_bp)

# -----------------------------
# 4️⃣ Fonctions utilitaires
# -----------------------------
def to_float(x):
    """Convertit proprement '10,50' ou Decimal/int/float en float."""
    if x in (None, ''):
        return 0.0
    try:
        return float(x)
    except Exception:
        s = str(x).strip().replace(' ', '').replace(',', '.')
        try:
            return float(s)
        except Exception:
            return 0.0

# -----------------------------
# 5️⃣ Configuration SEMOA
# -----------------------------
SEMOA_BASE = "https://api.semoa-payments.ovh/sandbox"
OAUTH2_CREDENTIALS = {
    "username": "api_cashpay.nsia",
    "password": "btCZkiiluA",
    "client_id": "api_cashpay.nsia",
    "client_reference": "tgIeTQpShnfewy33opbigMmhrtNqvTsj"
}

# -----------------------------
# 6️⃣ Routes questionnaire multi-étapes (sans doublons)
# -----------------------------
@app.route('/step1', methods=['GET', 'POST'])
def questionnaire_step1():
    form = Etape1Form()
    if form.validate_on_submit():
        session['duree_contrat'] = form.duree_contrat.data
        session['periode_debut'] = form.periode_debut.data.strftime('%Y-%m-%d') if form.periode_debut.data else None
        session['periode_fin'] = form.periode_fin.data.strftime('%Y-%m-%d') if form.periode_fin.data else None
        session['periodicite'] = form.periodicite.data
        session['prime_nette'] = to_float(form.prime_nette.data)
        session['accessoires'] = to_float(form.accessoires.data)
        session['taxes'] = to_float(form.taxes.data)
        session['prime_totale'] = round(session['prime_nette'] + session['accessoires'] + session['taxes'], 2)
        session['deces_accident'] = to_float(form.deces_accident.data)
        session['deces_toutes_causes'] = to_float(form.deces_toutes_causes.data)
        session['invalidite'] = to_float(form.invalidite.data)

        flash("Étape 1 enregistrée !", "success")
        return redirect(url_for('questionnaire_step2'))

    # Pré-remplissage depuis session
    if session.get('duree_contrat'):
        for field in ['duree_contrat', 'periode_debut', 'periode_fin', 'periodicite',
                      'prime_nette', 'accessoires', 'taxes', 'prime_totale',
                      'deces_accident', 'deces_toutes_causes', 'invalidite']:
            if field in session:
                value = session[field]
                if 'periode' in field or 'date' in field:
                    value = datetime.strptime(value, '%Y-%m-%d') if value else None
                setattr(form, field, type(getattr(form, field))(data=value))

    return render_template('step1.html', form=form)


@app.route('/step2', methods=['GET', 'POST'])
def questionnaire_step2():
    form = Etape2Form()
    if form.validate_on_submit():
        # Sauvegarde en session
        for prefix in ['assure', 'beneficiaire', 'souscripteur']:
            for field in form._fields:
                if field.startswith(prefix):
                    session[field] = getattr(form, field).data
        flash("Étape 2 enregistrée !", "success")
        return redirect(url_for('questionnaire_step3'))

    # Pré-remplissage
    for field in form._fields:
        if field in session:
            value = session[field]
            if 'date' in field:
                value = datetime.strptime(value, '%Y-%m-%d') if value else None
            setattr(form, field, type(getattr(form, field))(data=value))

    return render_template('step2.html', form=form)


@app.route('/step3', methods=['GET', 'POST'])
def questionnaire_step3():
    form = Etape3Form()
    if form.validate_on_submit():
        session['ack_conditions'] = form.ack_conditions.data
        session['lieu_signature'] = form.lieu_signature.data
        session['date_signature'] = form.date_signature.data.strftime('%Y-%m-%d') if form.date_signature.data else datetime.utcnow().strftime('%Y-%m-%d')
        flash("Étape 3 enregistrée ! Vous allez être redirigé vers le paiement.", "success")
        return redirect(url_for('paiement'))

    # Pré-remplissage
    for field in ['ack_conditions', 'lieu_signature', 'date_signature']:
        if field in session:
            value = session[field]
            if field == 'date_signature':
                value = datetime.strptime(value, '%Y-%m-%d') if value else None
            setattr(form, field, type(getattr(form, field))(data=value))

    return render_template('step3.html', form=form)

# -----------------------------
# 7️⃣ Route paiement
# -----------------------------
@app.route('/paiement', methods=['GET', 'POST'])
def paiement():
    # ... ta logique SEMOA ici (inchangée)
    return render_template('paiement.html', montant=session.get('prime_totale', 15000))

# -----------------------------
# 8️⃣ Routes génériques et export
# -----------------------------
@app.route('/')
def accueil():
    return render_template('home.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    form = SouscriptionForm()
    total = Subscription.query.count()
    if form.validate_on_submit():
        existing = Subscription.query.filter_by(telephone=form.telephone.data).first()
        if existing:
            flash("Ce numéro est déjà enregistré.", "danger")
        else:
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
    return render_template('index.html', form=form, total=total)

@app.route('/confirmation/<uuid>')
def confirmation(uuid):
    sub = Subscription.query.filter_by(uuid=uuid).first_or_404()
    return render_template('confirmation.html', subscription=sub)

@app.route('/export/csv')
def route_export_csv():
    return export_csv()

@app.route('/export/excel')
def route_export_excel():
    return export_excel()

@app.route('/manuel')
def manuel():
    return render_template('manuel.html')

# -----------------------------
# 9️⃣ Exécution
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
