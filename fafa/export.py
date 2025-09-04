from flask import Response
from models import QuestionnaireFafa
import csv
from io import StringIO
from openpyxl import Workbook
from io import BytesIO


# Export CSV
from flask import Response, session, redirect, url_for
from models import QuestionnaireFafa
import csv
from io import StringIO

def export_csv():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    questionnaires = QuestionnaireFafa.query.all()

    si = StringIO(newline='')
    writer = csv.writer(si)

    # Écrire les en-têtes
    writer.writerow([
        'ID',
        'Souscripteur - Nom', 'Souscripteur - Prénoms', 'Souscripteur - Tel', 'Souscripteur - Naissance', 'Souscripteur - Adresse',
        'Assuré - Nom', 'Assuré - Prénoms', 'Assuré - Tel', 'Assuré - Naissance', 'Assuré - Adresse',
        'Bénéficiaire - Nom', 'Bénéficiaire - Prénoms', 'Bénéficiaire - Tel', 'Bénéficiaire - Mail', 'Bénéficiaire - Adresse',
        'Profession', 'Droitier', 'Gaucher', 'Conditions acceptées', 'Type contrat'
    ])

    for q in questionnaires:
        writer.writerow([
            q.id,
            q.souscripteur_nom, q.souscripteur_prenoms, q.souscripteur_tel, q.souscripteur_date_naissance, q.souscripteur_adresse,
            q.assure_nom, q.assure_prenoms, q.assure_tel, q.assure_date_naissance, q.assure_adresse,
            q.beneficiaire_nom, q.beneficiaire_prenoms, q.beneficiaire_tel, q.beneficiaire_mail, q.beneficiaire_adresse,
            q.profession,
            'Oui' if q.est_droitier else 'Non',
            'Oui' if q.est_gaucher else 'Non',
            'Oui' if q.ack_conditions else 'Non',
            q.type_contrat
        ])

    output = si.getvalue().encode('utf-8')  # UTF-8 pour compatibilité avec Excel
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=questionnaires.csv"}
    )


from flask import send_file, session, redirect, url_for
from models import QuestionnaireFafa
from openpyxl import Workbook
from io import BytesIO

def export_excel():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    questionnaires = QuestionnaireFafa.query.all()
    wb = Workbook()
    ws = wb.active
    ws.title = "Questionnaires"

    # Entêtes
    ws.append([
        'ID',
        'Souscripteur - Nom', 'Souscripteur - Prénoms', 'Souscripteur - Tel', 'Souscripteur - Naissance', 'Souscripteur - Adresse',
        'Assuré - Nom', 'Assuré - Prénoms', 'Assuré - Tel', 'Assuré - Naissance', 'Assuré - Adresse',
        'Bénéficiaire - Nom', 'Bénéficiaire - Prénoms', 'Bénéficiaire - Tel', 'Bénéficiaire - Mail', 'Bénéficiaire - Adresse',
        'Profession', 'Droitier', 'Gaucher', 'Conditions acceptées', 'Type contrat'
    ])

    for q in questionnaires:
        ws.append([
            q.id,
            q.souscripteur_nom, q.souscripteur_prenoms, q.souscripteur_tel, q.souscripteur_date_naissance, q.souscripteur_adresse,
            q.assure_nom, q.assure_prenoms, q.assure_tel, q.assure_date_naissance, q.assure_adresse,
            q.beneficiaire_nom, q.beneficiaire_prenoms, q.beneficiaire_tel, q.beneficiaire_mail, q.beneficiaire_adresse,
            q.profession,
            'Oui' if q.est_droitier else 'Non',
            'Oui' if q.est_gaucher else 'Non',
            'Oui' if q.ack_conditions else 'Non',
            q.type_contrat
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name='questionnaires.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

