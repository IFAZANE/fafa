from flask import (
    Flask, render_template, request, session, send_file, redirect,
    flash, url_for
)
from config import Config
from models import db, QuestionnaireFafa, Paiement
from forms import Etape1Form, Etape2Form, Etape3Form
from admin import admin_bp
from export import export_csv, export_excel
import requests
import uuid
import os
from io import BytesIO
from datetime import datetime
from weasyprint import HTML
import json


# -----------------------------
# 1️⃣ Création de l'application
# -----------------------------
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.environ.get('SECRET_KEY', 'changeme')

# -----------------------------
# 2️⃣ Base de données
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
    if x in (None, ''):
        return 0.0
    try:
        return float(x)
    except:
        s = str(x).strip().replace(' ', '').replace(',', '.')
        try:
            return float(s)
        except:
            return 0.0

def parse_date(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    for fmt in ('%Y-%m-%d', '%a, %d %b %Y %H:%M:%S GMT'):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None

# -----------------------------
# 5️⃣ Configuration SEMOA OAuth 2.0
# -----------------------------
SEMOA_BASE = "https://api.semoa-payments.ovh/sandbox"
OAUTH2_CREDENTIALS = {
    "username": "api_cashpay.nsia",
    "password": "btCZkiiluA",
    "client_id": "api_cashpay.nsia",
    "client_secret": "tgIeTQpShnfewy33opbigMmhrtNqvTsj"
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

    if session.get('duree_contrat'):
        form.duree_contrat.data = session.get('duree_contrat')
        form.periode_debut.data = parse_date(session.get('periode_debut'))
        form.periode_fin.data = parse_date(session.get('periode_fin'))
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
        for prefix in ['assure', 'beneficiaire', 'souscripteur']:
            for field_name, field in form._fields.items():
                if field_name.startswith(prefix):
                    session[field_name] = getattr(form, field_name).data
        flash("Étape 2 enregistrée !", "success")
        return redirect(url_for('questionnaire_step3'))

    for field_name, field in form._fields.items():
        if field_name in session:
            value = session[field_name]
            if 'date' in field_name:
                value = parse_date(value)
            field.data = value

    return render_template('step2.html', form=form)

@app.route('/step3', methods=['GET', 'POST'])
def questionnaire_step3():
    form = Etape3Form()
    if form.validate_on_submit():
        session['ack_conditions'] = form.ack_conditions.data
        session['lieu_signature'] = form.lieu_signature.data
        session['date_signature'] = form.date_signature.data.strftime('%Y-%m-%d') if form.date_signature.data else datetime.utcnow().strftime('%Y-%m-%d')

        # Création du questionnaire Fafa en base
        questionnaire = QuestionnaireFafa(
            duree_contrat=session.get('duree_contrat'),
            periode_debut=parse_date(session.get('periode_debut')),
            periode_fin=parse_date(session.get('periode_fin')),
            periodicite=session.get('periodicite'),
            prime_nette=session.get('prime_nette'),
            accessoires=session.get('accessoires'),
            taxes=session.get('taxes'),
            prime_totale=session.get('prime_totale'),
            deces_accident=session.get('deces_accident'),
            deces_toutes_causes=session.get('deces_toutes_causes'),
            invalidite=session.get('invalidite'),
            ack_conditions=session.get('ack_conditions'),
            lieu_signature=session.get('lieu_signature'),
            date_signature=parse_date(session.get('date_signature'))
        )
        db.session.add(questionnaire)
        db.session.commit()
        session['questionnaire_id'] = questionnaire.id

        flash("Étape 3 enregistrée ! Vous allez être redirigé vers le paiement.", "success")
        return redirect(url_for('paiement'))

    if session.get('lieu_signature'):
        form.ack_conditions.data = session.get('ack_conditions', False)
        form.lieu_signature.data = session.get('lieu_signature')
        form.date_signature.data = parse_date(session.get('date_signature'))

    return render_template('step3.html', form=form)

# -----------------------------
# 7️⃣ Route paiement et insertion
# -----------------------------
# -----------------------------
# Route paiement
# -----------------------------
@app.route('/paiement', methods=['GET', 'POST'])
def paiement():
    montant = session.get('prime_totale')
    questionnaire_id = session.get('questionnaire_id')

    if montant is None or questionnaire_id is None:
        flash("Questionnaire ou montant introuvable. Veuillez compléter le questionnaire avant de payer.", "danger")
        return redirect(url_for('questionnaire_step1'))

    if request.method == 'POST':
        phone = request.form.get('phone')
        if not phone:
            flash("Veuillez saisir un numéro de téléphone valide.", "warning")
            return redirect(url_for('paiement'))

        try:
            montant_int = int(montant)
        except ValueError:
            flash("Montant invalide.", "danger")
            return redirect(url_for('paiement'))

        transaction_id = str(uuid.uuid4())
        session['transaction_id'] = transaction_id

        try:
            # 1. Authentification SEMOA
            auth_resp = requests.post(
                f"{SEMOA_BASE}/auth",
                json=OAUTH2_CREDENTIALS,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            auth_resp.raise_for_status()
            access_token = auth_resp.json().get('access_token')
            if not access_token:
                flash("Impossible d'obtenir le token SEMOA.", "danger")
                return redirect(url_for('paiement'))

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            # 2. Récupération des gateways
            gateways_resp = requests.get(f"{SEMOA_BASE}/gateways", headers=headers, timeout=10)
            gateways_resp.raise_for_status()
            gateways = gateways_resp.json()
            if not isinstance(gateways, list) or not gateways:
                flash("Aucune gateway disponible.", "danger")
                return redirect(url_for('paiement'))

            gateway_reference = gateways[0].get('reference')
            if not gateway_reference:
                flash("Référence de gateway introuvable.", "danger")
                return redirect(url_for('paiement'))

            # 3. Création de la commande de paiement
            payment_data = {
                "amount": montant_int,
                "currency": "XOF",
                "client": {"phone": phone},
                "gateway": {"reference": gateway_reference},
                "callback_url": url_for('confirmation_paiement', transaction_id=transaction_id, _external=True)
            }

            # 4. Appel à l'API SEMOA
            order_resp = requests.post(
                f"{SEMOA_BASE}/orders",
                json=payment_data,
                headers=headers,
                timeout=10
            )

            # Log pour débogage
            print("=== PAYLOAD ENVOYÉ ===")
            print(json.dumps(payment_data, ensure_ascii=False, indent=2))
            print("=== RÉPONSE SEMOA ===", order_resp.status_code)
            print(order_resp.text)

            order_resp.raise_for_status()
            order_data = order_resp.json()

            # 5. Enregistrement en base de données
            paiement = Paiement(
                questionnaire_fafa_id=questionnaire_id,
                transaction_id=transaction_id,
                amount=montant_int,
                currency="XOF",
                phone=phone,
                status=order_data.get('status', 'pending'),
                response=order_data
            )
            db.session.add(paiement)
            db.session.commit()

            # 6. Redirection vers l'URL de paiement
            gateway_url = order_data.get('bill_url') or order_data.get('gateway', {}).get('url')
            if not gateway_url:
                flash("Impossible de récupérer l'URL de paiement.", "danger")
                return redirect(url_for('paiement'))

            session['gateway_url'] = gateway_url
            flash(f"Paiement de {montant_int} XOF initié !", "success")
            return redirect(gateway_url)

        except requests.exceptions.RequestException as e:
            flash(f"Erreur SEMOA : {str(e)}", "danger")
            return redirect(url_for('paiement'))

        except Exception as e:
            flash(f"Erreur serveur : {str(e)}", "danger")
            return redirect(url_for('paiement'))

    return render_template('paiement.html', montant=montant)






# -----------------------------
# Route confirmation paiement
# -----------------------------
@app.route('/confirmation/<transaction_id>')
def confirmation_paiement(transaction_id):
    paiement = Paiement.query.filter_by(transaction_id=transaction_id).first()
    if not paiement:
        flash(f"Transaction {transaction_id} introuvable.", "warning")
        return redirect(url_for('questionnaire_step1'))

    # Vérifie si déjà confirmé
    if paiement.status != "confirmed":
        paiement.status = "confirmed"
        paiement.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f"Transaction {transaction_id} confirmée !", "success")
    else:
        flash(f"Transaction {transaction_id} était déjà confirmée.", "info")

    return redirect(url_for('questionnaire_step1'))

# -----------------------------
# Routes génériques et export
# -----------------------------
@app.route('/')
def accueil():
    session.clear()
    return render_template('home.html')

@app.route('/export/pdf')
def export_pdf():
    buffer = BytesIO()
    html = render_template('pdf_template.html', session=session)
    HTML(string=html).write_pdf(buffer)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="souscription.pdf", mimetype='application/pdf')

@app.route('/export/csv')
def route_export_csv():
    return export_csv()

@app.route('/export/excel')
def route_export_excel():
    return export_excel()

@app.route('/manuel')
def manuel():
    return render_template('manuel.html')


@app.route("/conditions")
def conditions():
    return render_template("conditions.html")


# -----------------------------
# Exécution
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)











