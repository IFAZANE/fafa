from flask import Response
from models import Subscription
import csv
from io import StringIO

def export_csv():
    subs = Subscription.query.all()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['UUID', 'Nom', 'Prénom', 'Téléphone', 'Ville', 'Produit'])

    for s in subs:
        cw.writerow([s.uuid, s.nom, s.prenom, s.telephone, s.ville, s.produit])

    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=subscribers.csv"})
