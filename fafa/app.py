from flask import Flask, render_template,request,session,send_file, redirect, flash, url_for, Response
from config import Config
from models import db, Subscription
from forms import SouscriptionForm, Etape1Form, Etape2Form, Etape3Form
from forms import QuestionnaireForm
from admin import admin_bp
import io
import os
import uuid
import csv
from io import StringIO, BytesIO
from openpyxl import Workbook
from weasyprint import HTML
from datetime import datetime
from weasyprint import HTML


from models import QuestionnaireFafa  # Assure-toi que c’est bien importé en haut

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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


def to_float(x):
    """Convertit proprement '10,50' ou Decimal ou int/float en float."""
    if x in (None, ''):
        return 0.0
    try:
        # si c'est Decimal/int/float
        return float(x)
    except Exception:
        s = str(x).strip().replace(' ', '').replace(',', '.')
        try:
            return float(s)
        except Exception:
            return 0.0

import uuid

#app = Flask(__name__)
app.secret_key = "secret-key"  # nécessaire pour utiliser session

# ✅ Step 1 : informations de l’assuré
from flask import Flask, render_template, request, session, redirect, url_for, flash
from forms import Etape1Form
from datetime import datetime

@app.route('/step1', methods=['GET', 'POST'])
def questionnaire_step1():
    form = Etape1Form()

    # Ne PAS effacer session ici -- sinon CSRF et valeurs sont perdues
    if form.validate_on_submit():
        session['duree_contrat'] = form.duree_contrat.data
        session['periode_debut'] = form.periode_debut.data.strftime('%Y-%m-%d') if form.periode_debut.data else None
        session['periode_fin'] = form.periode_fin.data.strftime('%Y-%m-%d') if form.periode_fin.data else None
        session['periodicite'] = form.periodicite.data

        pnet = to_float(form.prime_nette.data)
        acc  = to_float(form.accessoires.data)
        tax  = to_float(form.taxes.data)
        session['prime_nette'] = pnet
        session['accessoires'] = acc
        session['taxes'] = tax
        session['prime_totale'] = round(pnet + acc + tax, 2)

        session['deces_accident'] = to_float(form.deces_accident.data)
        session['deces_toutes_causes'] = to_float(form.deces_toutes_causes.data)
        session['invalidite'] = to_float(form.invalidite.data)

        flash("Étape 1 enregistrée !", "success")
        return redirect(url_for('questionnaire_step2'))  # attention au nom de la fonction pour step2

    # debug si validate_on_submit() = False après POST
    if request.method == 'POST' and not form.validate_on_submit():
        app.logger.debug("Step1 validation failed: %s", form.errors)
        flash(f"Erreur sur le formulaire (étape 1) : {form.errors}", "danger")

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

    # Ne PAS effacer session ici
    if form.validate_on_submit():
        session['assure_nom'] = form.assure_nom.data
        session['assure_prenoms'] = form.assure_prenoms.data
        session['assure_tel'] = form.assure_tel.data
        session['assure_date_naissance'] = form.assure_date_naissance.data.strftime('%Y-%m-%d') if form.assure_date_naissance.data else None
        session['assure_adresse'] = form.assure_adresse.data

        session['beneficiaire_nom'] = form.beneficiaire_nom.data
        session['beneficiaire_prenoms'] = form.beneficiaire_prenoms.data
        session['beneficiaire_tel'] = form.beneficiaire_tel.data
        session['beneficiaire_profession'] = form.beneficiaire_profession.data
        session['beneficiaire_adresse'] = form.beneficiaire_adresse.data

        session['souscripteur_nom'] = form.souscripteur_nom.data
        session['souscripteur_prenoms'] = form.souscripteur_prenoms.data
        session['souscripteur_tel'] = form.souscripteur_tel.data
        session['souscripteur_date_naissance'] = form.souscripteur_date_naissance.data.strftime('%Y-%m-%d') if form.souscripteur_date_naissance.data else None
        session['souscripteur_adresse'] = form.souscripteur_adresse.data

        flash("Étape 2 enregistrée !", "success")
        return redirect(url_for('questionnaire_step3'))

    if request.method == 'POST' and not form.validate_on_submit():
        app.logger.debug("Step2 validation failed: %s", form.errors)
        flash(f"Erreur sur le formulaire (étape 2) : {form.errors}", "danger")

    # Pré-remplissage si existant
    if session.get('assure_nom'):
        form.assure_nom.data = session.get('assure_nom')
        form.assure_prenoms.data = session.get('assure_prenoms')
        form.assure_tel.data = session.get('assure_tel')
        form.assure_date_naissance.data = datetime.strptime(session['assure_date_naissance'], '%Y-%m-%d') if session.get('assure_date_naissance') else None
        form.assure_adresse.data = session.get('assure_adresse')

        form.beneficiaire_nom.data = session.get('beneficiaire_nom')
        form.beneficiaire_prenoms.data = session.get('beneficiaire_prenoms')
        form.beneficiaire_tel.data = session.get('beneficiaire_tel')
        form.beneficiaire_profession.data = session.get('beneficiaire_profession')
        form.beneficiaire_adresse.data = session.get('beneficiaire_adresse')

        form.souscripteur_nom.data = session.get('souscripteur_nom')
        form.souscripteur_prenoms.data = session.get('souscripteur_prenoms')
        form.souscripteur_tel.data = session.get('souscripteur_tel')
        form.souscripteur_date_naissance.data = datetime.strptime(session['souscripteur_date_naissance'], '%Y-%m-%d') if session.get('souscripteur_date_naissance') else None
        form.souscripteur_adresse.data = session.get('souscripteur_adresse')

    return render_template('step2.html', form=form)


@app.route('/step3', methods=['GET', 'POST'])
def questionnaire_step3():
    form = Etape3Form()

    if form.validate_on_submit():
        # Sauvegarde en session
        session['ack_conditions'] = form.ack_conditions.data
        session['lieu_signature'] = form.lieu_signature.data
        session['date_signature'] = (
            form.date_signature.data.strftime('%Y-%m-%d')
            if form.date_signature.data else datetime.utcnow().strftime('%Y-%m-%d')
        )

        try:
            # Enregistrement en base
            souscription = QuestionnaireFafa(
                duree_contrat=session.get('duree_contrat'),
                periode_debut=datetime.strptime(session.get('periode_debut'), '%Y-%m-%d') if session.get('periode_debut') else None,
                periode_fin=datetime.strptime(session.get('periode_fin'), '%Y-%m-%d') if session.get('periode_fin') else None,
                periodicite=session.get('periodicite'),
                prime_nette=session.get('prime_nette'),
                accessoires=session.get('accessoires'),
                taxes=session.get('taxes'),
                prime_totale=session.get('prime_totale'),
                deces_accident=session.get('deces_accident'),
                deces_toutes_causes=session.get('deces_toutes_causes'),
                invalidite=session.get('invalidite'),
                assure_nom=session.get('assure_nom'),
                assure_prenoms=session.get('assure_prenoms'),
                assure_tel=session.get('assure_tel'),
                assure_date_naissance=datetime.strptime(session.get('assure_date_naissance'), '%Y-%m-%d') if session.get('assure_date_naissance') else None,
                assure_adresse=session.get('assure_adresse'),
                beneficiaire_nom=session.get('beneficiaire_nom'),
                beneficiaire_prenoms=session.get('beneficiaire_prenoms'),
                beneficiaire_tel=session.get('beneficiaire_tel'),
                beneficiaire_adresse=session.get('beneficiaire_adresse'),
                beneficiaire_profession=session.get('beneficiaire_profession'),
                souscripteur_nom=session.get('souscripteur_nom'),
                souscripteur_prenoms=session.get('souscripteur_prenoms'),
                souscripteur_tel=session.get('souscripteur_tel'),
                souscripteur_date_naissance=datetime.strptime(session.get('souscripteur_date_naissance'), '%Y-%m-%d') if session.get('souscripteur_date_naissance') else None,
                souscripteur_adresse=session.get('souscripteur_adresse'),
                ack_conditions=session.get('ack_conditions', False),
                lieu_signature=session.get('lieu_signature'),
                date_signature=datetime.strptime(session.get('date_signature'), '%Y-%m-%d') if session.get('date_signature') else datetime.utcnow()
            )
            db.session.add(souscription)
            db.session.commit()

            # Génération du PDF
            rendered = render_template('questionnaire_pdf.html', data=session)
            pdf_file = BytesIO()
            HTML(string=rendered).write_pdf(pdf_file)
            pdf_file.seek(0)

            session.clear()
            flash("Souscription enregistrée en base et PDF généré.", "success")

            return send_file(
                pdf_file,
                download_name="formulaire_FAFA.pdf",
                as_attachment=True,
                mimetype='application/pdf'
            )

        except Exception as e:
            db.session.rollback()
            app.logger.exception("Erreur enregistrement souscription")
            flash(f"Erreur lors de l'enregistrement en base : {str(e)}", "danger")
            return render_template('step3.html', form=form)  # ✅ garanti

    elif request.method == 'POST':
        # Formulaire envoyé mais non valide
        app.logger.debug("Step3 validation failed: %s", form.errors)
        flash(f"Erreur sur le formulaire (étape 3) : {form.errors}", "danger")

    # Pré-remplissage si existant
    if session.get('lieu_signature'):
        form.ack_conditions.data = session.get('ack_conditions', False)
        form.lieu_signature.data = session.get('lieu_signature')
        form.date_signature.data = (
            datetime.strptime(session['date_signature'], '%Y-%m-%d')
            if session.get('date_signature') else None
        )

    # ✅ garanti à 100% que form est passé au template
    return render_template('step3.html', form=form)



@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    form = QuestionnaireForm()

    if form.validate_on_submit():
        # 🔹 Sauvegarde en base
        try:
            nouvelle_souscription = QuestionnaireFafa(
                duree_contrat=form.duree_contrat.data,
                periode_debut=form.periode_debut.data,
                periode_fin=form.periode_fin.data,
                periodicite=form.periodicite.data,
                prime_nette=form.prime_nette.data,
                accessoires=form.accessoires.data,
                taxes=form.taxes.data,
                prime_totale=form.prime_totale.data,
                deces_accident=form.deces_accident.data,
                deces_toutes_causes=form.deces_toutes_causes.data,
                invalidite=form.invalidite.data,
                hospitalisation=form.hospitalisation.data,
                traitement_medical=form.traitement_medical.data,
                indemnite_journaliere=form.indemnite_journaliere.data,
                assure_nom=form.assure_nom.data,
                assure_prenoms=form.assure_prenoms.data,
                assure_tel=form.assure_tel.data,
                assure_date_naissance=form.assure_date_naissance.data,
                assure_adresse=form.assure_adresse.data,
                beneficiaire_nom=form.beneficiaire_nom.data,
                beneficiaire_prenoms=form.beneficiaire_prenoms.data,
                beneficiaire_tel=form.beneficiaire_tel.data,
                beneficiaire_adresse=form.beneficiaire_adresse.data,
                beneficiaire_profession=form.beneficiaire_profession.data,
                beneficiaire_lateralite=form.beneficiaire_lateralite.data,
                souscripteur_nom=form.souscripteur_nom.data,
                souscripteur_prenoms=form.souscripteur_prenoms.data,
                souscripteur_tel=form.souscripteur_tel.data,
                souscripteur_date_naissance=form.souscripteur_date_naissance.data,
                souscripteur_adresse=form.souscripteur_adresse.data,
                ack_conditions=form.ack_conditions.data,
                lieu_signature=form.lieu_signature.data,
                date_signature=form.date_signature.data or datetime.utcnow()
            )
            db.session.add(nouvelle_souscription)
            db.session.commit()
            flash("Souscription enregistrée avec succès !", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'enregistrement : {str(e)}", "error")
            return render_template('questionnaire.html', form=form)

        # 🔹 Génération du PDF
        rendered = render_template('questionnaire_pdf.html', form=form)
        pdf_file = BytesIO()
        HTML(string=rendered).write_pdf(pdf_file)
        pdf_file.seek(0)

        return send_file(
            pdf_file,
            download_name="formulaire_FAFA.pdf",
            as_attachment=True,
            mimetype='application/pdf'
        )

    return render_template('questionnaire.html', form=form)

@app.route('/questionnaire/pdf/<int:id>')
def generate_pdf(id):
    q = QuestionnaireFafa.query.get_or_404(id)
    html = render_template('questionnaire_pdf.html', form=q, current_year=date.today().year)
    pdf = HTML(string=html).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=questionnaire_{id}.pdf'
    return response


@app.route('/confirmation1')
def confirmation1():
    return render_template('confirmation1.html', data=session)

@app.route('/download_pdf')
def download_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("CONTRAT FAFA - Souscription", styles["Title"]))
    story.append(Spacer(1, 12))

    for key, value in session.items():
        story.append(Paragraph(f"<b>{key.replace('_',' ').capitalize()}:</b> {value}", styles["Normal"]))
        story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="contrat_fafa.pdf", mimetype="application/pdf")

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































