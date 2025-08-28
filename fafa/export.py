from flask import Response
from models import Subscription
import csv
from io import StringIO, BytesIO
from openpyxl import Workbook

def export_csv():
    subs = Subscription.query.all()
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['UUID', 'Nom', 'Prénom', 'Téléphone', 'Ville', 'Produit'])
    for s in subs:
        writer.writerow([s.uuid, s.nom, s.prenom, s.telephone, s.ville, s.produit])
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=subscriptions.csv"}
    )

def export_excel():
    subs = Subscription.query.all()
    wb = Workbook()
    ws = wb.active
    ws.append(['UUID', 'Nom', 'Prénom', 'Téléphone', 'Ville', 'Produit'])
    for s in subs:
        ws.append([s.uuid, s.nom, s.prenom, s.telephone, s.ville, s.produit])
    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    return Response(
        bio.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=subscriptions.xlsx"}
    )
