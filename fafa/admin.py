from flask import Blueprint, render_template, redirect, url_for, request, session, flash, Response, send_file
from models import Subscription
from io import StringIO, BytesIO
from collections import Counter
import csv
import pandas as pd

#admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash("Identifiants incorrects", 'error')
    return render_template('login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin.login'))

from collections import defaultdict

def aggregate_city_data(rows):
    data = defaultdict(int)
    for row in rows:
        data[row.city] += 1  # ou row.subscription_count selon votre modèle
    return list(data.keys()), list(data.values())


from flask import Blueprint, render_template
from models import QuestionnaireFafa
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def dashboard():
    contrats = QuestionnaireFafa.query.with_entities(QuestionnaireFafa.type_contrat, func.count()).group_by(QuestionnaireFafa.type_contrat).all()
    villes = QuestionnaireFafa.query.with_entities(QuestionnaireFafa.souscripteur_adresse, func.count()).group_by(QuestionnaireFafa.souscripteur_adresse).all()

    product_labels = [c[0] for c in contrats]
    product_counts = [c[1] for c in contrats]

    city_labels = [v[0] if v[0] else "Inconnu" for v in villes]
    city_counts = [v[1] for v in villes]

    return render_template("admin_dashboard.html",
        total=sum(product_counts),
        product_labels=product_labels,
        product_counts=product_counts,
        city_labels=city_labels,
        city_counts=city_counts
    )


@admin_bp.route('/export/csv')
def export_csv():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    data = QuestionnaireFafa.query.all()
    si = StringIO()
    writer = csv.writer(si)

    writer.writerow([
        'ID', 'Souscripteur Nom', 'Souscripteur Prénoms', 'Souscripteur Tel', 'Souscripteur Adresse', 'Souscripteur Date Naissance',
        'Assuré Nom', 'Assuré Prénoms', 'Assuré Tel', 'Assuré Adresse', 'Assuré Date Naissance',
        'Bénéficiaire Nom', 'Bénéficiaire Prénoms', 'Bénéficiaire Tel', 'Bénéficiaire Mail', 'Bénéficiaire Adresse',
        'Profession', 'Est Droitier', 'Est Gaucher', 'Type Contrat', 'Conditions Acceptées'
    ])

    for q in data:
        writer.writerow([
            q.id,
            q.souscripteur_nom,
            q.souscripteur_prenoms,
            q.souscripteur_tel,
            q.souscripteur_adresse,
            q.souscripteur_date_naissance,
            q.assure_nom,
            q.assure_prenoms,
            q.assure_tel,
            q.assure_adresse,
            q.assure_date_naissance,
            q.beneficiaire_nom,
            q.beneficiaire_prenoms,
            q.beneficiaire_tel,
            q.beneficiaire_mail,
            q.beneficiaire_adresse,
            q.profession,
            q.est_droitier,
            q.est_gaucher,
            q.type_contrat,
            q.ack_conditions
        ])

    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=souscriptions.csv"})


@admin_bp.route('/export/excel')
def export_excel():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    data = QuestionnaireFafa.query.all()
    rows = []

    for q in data:
        rows.append({
            "ID": q.id,
            "Souscripteur Nom": q.souscripteur_nom,
            "Souscripteur Prénoms": q.souscripteur_prenoms,
            "Souscripteur Tel": q.souscripteur_tel,
            "Souscripteur Adresse": q.souscripteur_adresse,
            "Souscripteur Date Naissance": q.souscripteur_date_naissance,
            "Assuré Nom": q.assure_nom,
            "Assuré Prénoms": q.assure_prenoms,
            "Assuré Tel": q.assure_tel,
            "Assuré Adresse": q.assure_adresse,
            "Assuré Date Naissance": q.assure_date_naissance,
            "Bénéficiaire Nom": q.beneficiaire_nom,
            "Bénéficiaire Prénoms": q.beneficiaire_prenoms,
            "Bénéficiaire Tel": q.beneficiaire_tel,
            "Bénéficiaire Mail": q.beneficiaire_mail,
            "Bénéficiaire Adresse": q.beneficiaire_adresse,
            "Profession": q.profession,
            "Est Droitier": q.est_droitier,
            "Est Gaucher": q.est_gaucher,
            "Type Contrat": q.type_contrat,
            "Conditions Acceptées": q.ack_conditions
        })

    df = pd.DataFrame(rows)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Souscriptions')

    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        download_name='souscriptions.xlsx',
        as_attachment=True
    )






