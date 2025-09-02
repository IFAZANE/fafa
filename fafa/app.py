from flask import (
    Flask, render_template, request, session, send_file, redirect,
    flash, url_for, make_response
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
from io import BytesIO
from datetime import datetime, date
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
# 6️⃣ Routes questionnaire multi-étapes
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
        form.duree_contrat.data = session.get('duree_contrat')
        form.periode_debut.data = datetime.strptime(session['periode_debut'], '%Y-%m-%d') if session.get('periode_debut') else None
        form.periode_fin.data = datetime.strptime(session['periode_fin'], '%Y-%m-%d') if session.get('periode_fin') else None
        form.periodicite.data = session.get('periodicite')
        form.prime_nette.data = session.get('prime_nette')
        form.accessoires.data = session.get('accessoires')
        form.taxes.data = session.get('taxes')
        form.prime_totale.data = session.get('prime_totale')
        form.deces_accident.data = session.get('deces_accident')
        form.deces_toutes_causes.data = session.get('deces_toutes_causes')
        form.invalidite.data = session.get('invalidite')

    return render_template('step1.html', form=form)

@app.route('/step2', methods=['GET', 'POST'])
def questionnaire_step2():
    form = Etape2Form()
    if form.validate_on_submit():
        # Sauvegarde en session
        for prefix in ['assure', 'beneficiaire', 'souscripteur']:
            for field_name, field in form._fields.items():
                if field_name.startswith(prefix):
                    session[field_name] = getattr(form, field_name).data
        flash("Étape 2 enregistrée !", "success")
        return redirect(url_for('questionnaire_step3'))

    # Pré-remplissage
    for field_name, field in form._fields.items():
        if field_name in session:
            value = session[field_name]
            if 'date' in field_name:
                value = datetime.strptime(value, '%Y-%m-%d') if value else None
            setattr(form, field_name, type(field)(data=value))

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
    if session.get('lieu_signature'):
        form.ack_conditions.data = session.get('ack_conditions', False)
        form.lieu_signature.data = session.get('lieu_signature')
        form.date_signature.data = datetime.strptime(session['date_signature'], '%Y-%m-%d') if session.get('date_signature') else None

    return render_template('step3.html', form=form)

# -----------------------------
# 7️⃣ Route paiement
# -----------------------------
@app.route('/paiement', methods=['GET', 'POST'])
def paiement():
    if request.method == 'POST':
        montant = session.get('prime_totale', 15000)
        phone = request.form.get('phone')
        transaction_id = str(uuid.uuid4())
        session['transaction_id'] = transaction_id

        # ✅ Auth OAuth SEMOA corrigé
        headers = {"Content-Type": "application/json"}
        auth_resp = requests.post(
            f"{SEMOA_BASE}/oauth/token",
            json={
                "grant_type": "password",
                "username": OAUTH2_CREDENTIALS['username'],
                "password": OAUTH2_CREDENTIALS['password'],
                "client_id": OAUTH2_CREDENTIALS['client_id']
            },
            headers=headers
        )

        if auth_resp.status_code != 200:
            flash("Erreur OAuth SEMOA : " + auth_resp.text, "danger")
            return redirect(url_for('paiement'))

        access_token = auth_resp.json().get('access_token')
        payment_data = {
            "amount": montant,
            "currency": "XOF",
            "payment_method": "mobilemoney",
            "phone": phone,
            "client_reference": OAUTH2_CREDENTIALS['client_reference'],
            "transaction_id": transaction_id
        }
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        pay_resp = requests.post(f"{SEMOA_BASE}/payments", json=payment_data, headers=headers)

        if pay_resp.status_code in (200, 201):
            flash("Paiement initié avec succès !", "success")
            return redirect(url_for('confirmation_paiement', transaction_id=transaction_id))
        else:
            flash("Erreur lors de la création du paiement : " + pay_resp.text, "danger")

    return render_template('paiement.html', montant=session.get('prime_totale', 15000))


def confirmation_paiement(transaction_id):
    # Pour sandbox, status simulé
    status = "success"
    if status != "success":
        flash("Paiement non encore validé.", "warning")
        return redirect(url_for('paiement'))

    try:
        def get_date(key):
            val = session.get(key)
            return datetime.strptime(val, '%Y-%m-%d') if val else None

        def get_float(key):
            return to_float(session.get(key))

        souscription = Subscription(
            uuid=session.get('transaction_id'),
            nom=session.get('assure_nom'),
            prenom=session.get('assure_prenom'),
            telephone=session.get('assure_telephone'),
            produit=session.get('produit', '15 000 FCFA/an'),
            duree_contrat=session.get('duree_contrat'),
            date_debut=get_date('periode_debut'),
            date_fin=get_date('periode_fin'),
            periodicite=session.get('periodicite'),
            prime_totale=get_float('prime_totale')
        )
        db.session.add(souscription)
        db.session.commit()
    except Exception as e:
        flash(f"Erreur sauvegarde : {e}", "danger")

    flash("Paiement confirmé et souscription enregistrée !", "success")
    return render_template('confirmation.html', subscription=souscription)

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
# 9️⃣ Génération PDF depuis questionnaire
# -----------------------------
@app.route('/export/pdf')
def export_pdf():
    buffer = BytesIO()
    html = render_template('pdf_template.html', session=session)
    HTML(string=html).write_pdf(buffer)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="souscription.pdf", mimetype='application/pdf')

# -----------------------------
# 10️⃣ Exécution
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)

