from flask import Flask, render_template,request,session,send_file, redirect, flash, url_for, Response
from config import Config
from models import db, Subscription
from forms import SouscriptionForm
from forms import QuestionnaireForm
from admin import admin_bp
import os
import uuid
import csv
from io import StringIO, BytesIO
from openpyxl import Workbook
from weasyprint import HTML
from datetime import datetime

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


@app.route("/questionnaire", methods=["GET", "POST"])
def questionnaire():
    form = QuestionnaireForm()
    if form.validate_on_submit():
        # TODO: insérer en base (SQLAlchemy ou SQL brut)
        flash("Souscription enregistrée", "success")
        return redirect(url_for("questionnaire"))
    return render_template("questionnaire.html", form=form)





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


















