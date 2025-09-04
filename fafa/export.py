from flask import Response
from models import QuestionnaireFafa
import csv
from io import StringIO
from openpyxl import Workbook
from io import BytesIO


# Export CSV
def export_csv():
    questionnaires = QuestionnaireFafa.query.all()
    si = StringIO()
    cw = csv.writer(si)

    cw.writerow([
        'ID',
        'Souscripteur - Nom', 'Souscripteur - Prénoms', 'Souscripteur - Tel', 'Souscripteur - Naissance', 'Souscripteur - Adresse',
        'Assuré - Nom', 'Assuré - Prénoms', 'Assuré - Tel', 'Assuré - Naissance', 'Assuré - Adresse',
        'Bénéficiaire - Nom', 'Bénéficiaire - Prénoms', 'Bénéficiaire - Tel', 'Bénéficiaire - Mail', 'Bénéficiaire - Adresse',
        'Profession', 'Droitier', 'Gaucher', 'Conditions acceptées', 'Type contrat'
    ])

    for q in questionnaires:
        cw.writerow([
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

    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=questionnaires.csv"}
    )


# Export Excel
def export_excel():
    questionnaires = QuestionnaireFafa.query.all()
    wb = Workbook()
    ws = wb.active
    ws.title = "Questionnaires"

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

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)

    return Response(
        bio.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=questionnaires.xlsx"}
    )
