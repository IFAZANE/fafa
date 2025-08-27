from flask import Blueprint, render_template, redirect, url_for, request, session, flash, Response, send_file
from models import Subscription
from io import StringIO, BytesIO
import csv
import pandas as pd

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

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

@admin_bp.route('/')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    total = Subscription.query.count()
    return render_template('admin_dashboard.html', total=total)

@admin_bp.route('/export/csv')
def export_csv():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    subs = Subscription.query.all()
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['UUID', 'Nom', 'Prénom', 'Téléphone', 'Ville', 'Produit'])
    for s in subs:
        writer.writerow([s.uuid, s.nom, s.prenom, s.telephone, s.ville, s.produit])
    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=subscriptions.csv"})

@admin_bp.route('/export/excel')
def export_excel():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    subs = Subscription.query.all()
    data = [{
        "UUID": s.uuid,
        "Nom": s.nom,
        "Prénom": s.prenom,
        "Téléphone": s.telephone,
        "Ville": s.ville,
        "Produit": s.produit
    } for s in subs]

    df = pd.DataFrame(data)

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
