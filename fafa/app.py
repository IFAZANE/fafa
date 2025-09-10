from flask import (
    Flask, render_template, request, session, send_file, redirect,
    flash, url_for
)
from config import Config
from models import db, QuestionnaireFafa, Paiement
from forms import Etape1Form, Etape2Form
from admin import admin_bp
from export import export_csv, export_excel
import requests
import uuid
import os
from io import BytesIO
from datetime import datetime
from weasyprint import HTML
import json
import re


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
        # Sauvegarde dans la session
        session['souscripteur'] = {
            'nom': form.souscripteur_nom.data,
            'prenoms': form.souscripteur_prenoms.data,
            'tel': form.souscripteur_tel.data,
            'date_naissance': form.souscripteur_date_naissance.data.strftime('%Y-%m-%d'),
            'adresse': form.souscripteur_adresse.data
        }
        session['assure'] = {
            'nom': form.assure_nom.data,
            'prenoms': form.assure_prenoms.data,
            'tel': form.assure_tel.data,
            'date_naissance': form.assure_date_naissance.data.strftime('%Y-%m-%d'),
            'adresse': form.assure_adresse.data
        }

        flash("Étape 1 enregistrée avec succès !", "success")
        return redirect(url_for('questionnaire_step2'))

    # Préremplissage depuis la session
    if 'souscripteur' in session:
        form.souscripteur_nom.data = session['souscripteur'].get('nom')
        form.souscripteur_prenoms.data = session['souscripteur'].get('prenoms')
        form.souscripteur_tel.data = session['souscripteur'].get('tel')
        form.souscripteur_date_naissance.data = parse_date(session['souscripteur'].get('date_naissance'))
        form.souscripteur_adresse.data = session['souscripteur'].get('adresse')

    if 'assure' in session:
        form.assure_nom.data = session['assure'].get('nom')
        form.assure_prenoms.data = session['assure'].get('prenoms')
        form.assure_tel.data = session['assure'].get('tel')
        form.assure_date_naissance.data = parse_date(session['assure'].get('date_naissance'))
        form.assure_adresse.data = session['assure'].get('adresse')

    return render_template('step1.html', form=form)


@app.route('/step2', methods=['GET', 'POST'])
def questionnaire_step2():
    form = Etape2Form()

    if form.validate_on_submit():
        # Création du questionnaire en base
        q = QuestionnaireFafa(
            souscripteur_nom=session['souscripteur']['nom'],
            souscripteur_prenoms=session['souscripteur']['prenoms'],
            souscripteur_date_naissance=parse_date(session['souscripteur']['date_naissance']),
            souscripteur_tel=session['souscripteur']['tel'],
            souscripteur_adresse=session['souscripteur']['adresse'],
            assure_nom=session['assure']['nom'],
            assure_prenoms=session['assure']['prenoms'],
            assure_date_naissance=parse_date(session['assure']['date_naissance']),
            assure_tel=session['assure']['tel'],
            assure_adresse=session['assure']['adresse'],
            beneficiaire_nom=form.beneficiaire_nom.data,
            beneficiaire_prenoms=form.beneficiaire_prenoms.data,
            beneficiaire_tel=form.beneficiaire_tel.data,
            beneficiaire_mail=form.beneficiaire_mail.data,
            beneficiaire_adresse=form.beneficiaire_adresse.data,
            profession=form.profession.data,
            est_droitier=form.est_droitier.data,
            est_gaucher=form.est_gaucher.data,
            ack_conditions=form.conditions_acceptees.data,
            type_contrat=form.choix_fafa.data,
            statut="pending"
        )
        db.session.add(q)
        db.session.commit()

        session['questionnaire_id'] = q.id
        session['type_contrat'] = form.choix_fafa.data

        flash("Étape 2 enregistrée avec succès !", "success")
        return redirect(url_for('paiement'))

    return render_template('step2.html', form=form)


# -----------------------------
# 7️⃣ Route paiement
# -----------------------------
@app.route('/paiement', methods=['GET', 'POST'])
def paiement():
    montant = session.get('type_contrat')
    q_id = session.get('questionnaire_id')

    if not montant or not q_id:
        flash("Veuillez compléter le questionnaire avant de payer.", "danger")
        return redirect(url_for('questionnaire_step2'))

    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        if not re.fullmatch(r"\+228\d{8}", phone):
            flash("Numéro invalide. Format : +228XXXXXXXX.", "warning")
            return redirect(url_for('paiement'))

        montant_int = int(montant)
        transaction_id = str(uuid.uuid4())
        session['transaction_id'] = transaction_id

        # Auth SEMOA
        try:
            auth_resp = requests.post(f"{SEMOA_BASE}/auth", json=OAUTH2_CREDENTIALS, headers={"Content-Type": "application/json"}, timeout=10)
            auth_resp.raise_for_status()
            access_token = auth_resp.json().get('access_token')
            if not access_token:
                flash("Impossible d'obtenir le token SEMOA.", "danger")
                return redirect(url_for('paiement'))

            headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
            gateways_resp = requests.get(f"{SEMOA_BASE}/gateways", headers=headers, timeout=10)
            gateways_resp.raise_for_status()
            gateway_reference = gateways_resp.json()[0].get('reference')

            payment_data = {
                "amount": montant_int,
                "currency": "XOF",
                "client": {"phone": phone},
                "gateway": {"reference": gateway_reference},
                "callback_url": url_for('confirmation_paiement', transaction_id=transaction_id, _external=True),
                "merchant_reference": transaction_id,
                "description": "Souscription FAFA"
            }

            order_resp = requests.post(f"{SEMOA_BASE}/orders", json=payment_data, headers=headers, timeout=10)
            order_resp.raise_for_status()
            order_data = order_resp.json()

            # Sauvegarde paiement lié au questionnaire
            paiement = Paiement(
                transaction_id=transaction_id,
                amount=montant_int,
                currency="XOF",
                phone=phone,
                status=order_data.get('status', 'pending'),
                response=order_data,
                questionnaire_fafa_id=q_id
            )
            db.session.add(paiement)
            db.session.commit()

            gateway_url = order_data.get('bill_url') or order_data.get('gateway', {}).get('url')
            if not gateway_url:
                flash("Impossible de récupérer l'URL de paiement.", "danger")
                return redirect(url_for('paiement'))

            flash(f"Paiement de {montant_int} XOF initié !", "success")
            return redirect(gateway_url)

        except Exception as e:
            flash(f"Erreur paiement : {str(e)}", "danger")
            return redirect(url_for('paiement'))

    return render_template('paiement.html', montant=montant)


# -----------------------------
# 8️⃣ Confirmation paiement
# -----------------------------
@app.route('/confirmation/<transaction_id>')
def confirmation_paiement(transaction_id):
    paiement = Paiement.query.filter_by(transaction_id=transaction_id).first()
    if not paiement:
        flash("Transaction introuvable.", "danger")
        return redirect(url_for('questionnaire_step2'))

    if paiement.status != "confirmed":
        paiement.status = "confirmed"
        paiement.updated_at = datetime.utcnow()

        q = QuestionnaireFafa.query.get(paiement.questionnaire_fafa_id)
        if q:
            q.statut = "confirmed"

        db.session.commit()

    questionnaire = QuestionnaireFafa.query.get(paiement.questionnaire_fafa_id)
    html = render_template('questionnaire_pdf.html', questionnaire=questionnaire)
    buffer = BytesIO()
    HTML(string=html).write_pdf(buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"souscription_{questionnaire.id}.pdf",
        mimetype='application/pdf'
    )


# -----------------------------
# Routes génériques et export
# -----------------------------
@app.route('/')
def accueil():
    session.clear()
    return render_template('home.html')


@app.route('/questionnaire_pdf')
def questionnaire_pdf():
    return render_template('questionnaire_pdf.html')


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

