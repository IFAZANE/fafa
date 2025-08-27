from flask import Flask, render_template, redirect, url_for, flash
from config import Config
from models import db, Subscription
from forms import SubscriptionForm

import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('postgresql://fafadb_user:yWH0gommUR5p2YCX7Yh4ZqMSG3ww9gEU@dpg-d2njb4ggjchc7386ikhg-a/fafadb')
db = SQLAlchemy(app)


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


from admin import admin_bp
app.register_blueprint(admin_bp)

app.secret_key = 'changeme'  # Pour les sessions sécurisées


@app.route('/', methods=['GET', 'POST'])
def index():
    form = SubscriptionForm()
    total = Subscription.query.count()

    if form.validate_on_submit():
        sub = Subscription(
            nom=form.nom.data,
            prenom=form.prenom.data,
            telephone=form.telephone.data,
            ville=form.ville.data,
            produit=form.produit.data
        )
        db.session.add(sub)
        db.session.commit()
        return render_template('confirmation.html', uuid=sub.uuid)

    return render_template('index.html', form=form, total=total)

from export import export_csv
app.add_url_rule('/export', 'export_csv', export_csv)

if __name__ == '__main__':
    app.run(debug=True)

