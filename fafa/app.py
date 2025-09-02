from flask import (
    Flask, render_template, request, session, send_file, redirect,
    flash, url_for
)
from config import Config
from models import db, QuestionnaireFafa  # ✅ remplacer Subscription par QuestionnaireFafa
from forms import Etape1Form, Etape2Form, Etape3Form
from admin import admin_bp
from export import export_csv, export_excel
import requests
import uuid
import os
from io import BytesIO
from datetime import datetime
from weasyprint import HTML

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
    'postgresql://fafadb_user:password@host:port/fafadb'
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
SEMOA_BASE = "https://api.semoa-payments.ovh/sandbox/"
OAUTH2_CREDENTIALS = {
    "username": "api_cashpay.nsia",
    "password": "btCZkiiluA",
    "client_id": "api_cashpay.nsia",
    "client_secret": "tgIeTQpShnfewy33opbigMmhrtNqvTsj"
}

# -----------------------------
# 6️⃣ Routes questionnaire multi-étapes
# -----------------------------
# ... Étapes 1, 2, 3 inchangées ...

# -----------------------------
# 7️⃣ Route paiement avec SEMOA OAuth 2.0 et insertion en base
# -----------------------------
@app.route('/paiement', methods=['GET', 'POST'])
def paiement():
    montant = session.get('prime_totale')
    if montant is None:
        flash("Montant introuvable. Veuillez recommencer la souscription.", "danger")
        return redirect(url_for('questionnaire_step1'))

    if request.method == 'POST':
        phone = request.form.get('phone')
        if not phone:
            flash("Veuillez saisir un numéro de téléphone valide.", "warning")
            return redirect(url_for('paiement'))

        transaction_id = str(uuid.uuid4())
        session['transaction_id'] = transaction_id

        try:
            # Auth SEMOA
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

            headers = {"Authorization": f"Bearer {access_token}"}

            # Récupération des gateways disponibles
            gateways_resp = requests.get(f"{SEMOA_BASE}/gateways", headers=headers, timeout=10)
            gateways_resp.raise_for_status()
            gateways = gateways_resp.json()
            if not gateways:
                flash("Aucune gateway disponible.", "danger")
                return redirect(url_for('paiement'))

            gateway_id = gateways[0]['id']

            # Création de la commande
            payment_data = {
                "amount": int(montant),
                "currency": "XOF",
                "client": {"phone": phone},
                "gateway": {"id": gateway_id},
                "callback_url": url_for('confirmation_paiement', transaction_id=transaction_id, _external=True)
            }

            order_resp = requests.post(f"{SEMOA_BASE}/orders", json=payment_data, headers=headers, timeout=10)
            order_resp.raise_for_status()
            order_data = order_resp.json()

            # ✅ Enregistrement dans la table questionnaire_fafa
            transaction = QuestionnaireFafa(
                transaction_id=transaction_id,
                phone=phone,
                amount=montant,
                currency="XOF",
                order_reference=order_data.get('order_reference'),
                bill_url=order_data.get('bill_url'),
                status=order_data.get('status')
            )
            db.session.add(transaction)
            db.session.commit()

            # Redirection vers le lien de paiement SEMOA
            session['gateway_url'] = order_data.get('bill_url') or order_data.get('gateway', {}).get('url')
            flash(f"Paiement de {montant} XOF initié !", "success")
            return redirect(session['gateway_url'])

        except requests.exceptions.RequestException as e:
            flash(f"Erreur SEMOA : {str(e)}", "danger")
            return redirect(url_for('paiement'))

    return render_template('paiement.html', montant=montant)

# -----------------------------
# 8️⃣ Confirmation paiement et mise à jour status
# -----------------------------
@app.route('/confirmation/<transaction_id>')
def confirmation_paiement(transaction_id):
    transaction = QuestionnaireFafa.query.filter_by(transaction_id=transaction_id).first()
    if transaction:
        transaction.status = "confirmed"
        db.session.commit()
        flash(f"Transaction {transaction_id} confirmée !", "success")
    else:
        flash(f"Transaction {transaction_id} introuvable.", "warning")
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

# -----------------------------
# Exécution
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)

























