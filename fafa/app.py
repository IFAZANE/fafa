from flask import Flask, render_template, redirect, flash, url_for, Response
from config import Config
from models import db, Subscription
from forms import SouscriptionForm, QuestionnaireForm
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
    return redirect(url_for('step1'))

@app.route('/step1', methods=['GET', 'POST'])
def step1():
    if request.method == 'POST':
        session['souscripteur_nom'] = request.form['souscripteur_nom']
        session['souscripteur_prenom'] = request.form['souscripteur_prenom']
        session['souscripteur_tel'] = request.form['souscripteur_tel']
        session['souscripteur_naissance'] = request.form['souscripteur_naissance']
        session['souscripteur_adresse'] = request.form['souscripteur_adresse']
        return redirect(url_for('step2'))
    return render_template('step1.html')

@app.route('/step2', methods=['GET', 'POST'])
def step2():
    if request.method == 'POST':
        session['assure_nom'] = request.form['assure_nom']
        session['assure_prenom'] = request.form['assure_prenom']
        session['assure_tel'] = request.form['assure_tel']
        session['assure_naissance'] = request.form['assure_naissance']
        session['assure_adresse'] = request.form['assure_adresse']
        return redirect(url_for('step3'))
    return render_template('step2.html')

@app.route('/step3', methods=['GET', 'POST'])
def step3():
    if request.method == 'POST':
        session['beneficiaire_nom'] = request.form['beneficiaire_nom']
        session['beneficiaire_prenom'] = request.form['beneficiaire_prenom']
        session['beneficiaire_tel'] = request.form['beneficiaire_tel']
        session['beneficiaire_adresse'] = request.form['beneficiaire_adresse']
        return redirect(url_for('confirmation'))
    return render_template('step3.html')

@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html', data=session)

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










