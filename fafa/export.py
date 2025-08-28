from flask import Response
from models import Subscription
import csv
from io import StringIO
from openpyxl import Workbook
from io import BytesIO

# Export CSV
def export_csv():
    subs = Subscription.query.all()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['UUID', 'Nom', 'Prénom', 'Téléphone', 'Ville', 'Produit'])

    for s in subs:
        produit = s.produit if s.produit else ""
        cw.writerow([s.uuid, s.nom, s.prenom, s.telephone, s.ville, produit])

    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=subscriptions.csv"}
    )

# Export Excel
def export_excel():
    subs = Subscription.query.all()
    wb = Workbook()
    ws = wb.active
    ws.append(['UUID', 'Nom', 'Prénom', 'Téléphone', 'Ville', 'Produit'])

    for s in subs:
        produit = s.produit if s.produit else ""
        ws.append([s.uuid, s.nom, s.prenom, s.telephone, s.ville, produit])

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)

    return Response(
        bio.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=subscriptions.xlsx"}
    )
