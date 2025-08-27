from flask import Flask, render_template
from config import Config
from models import db, Subscription
from forms import SubscriptionForm
from admin import admin_bp
from export import export_csv
import os

# 1️⃣ Créer l'application Flask (une seule fois)
app = Flask(__name__)
app.config.from_object(Config)

# 2️⃣ Configurer SQLAlchemy correctement
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://fafadb_user:yWH0gommUR5p2YCX7Yh4ZqMSG3ww9gEU@dpg-d2njb4ggjchc7386ikhg-a.oregon-postgres.render.com:5432/fafadb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3️⃣ Attacher db à l'application (une seule instance)
db.init_app(app)

# 4️⃣ Créer les tables si elles n'existent pas
with app.app_context():
    db.create_all()

# 5️⃣ Enregistrer les blueprints
app.register_blueprint(admin_bp)

# 6️⃣ Clé secrète pour les sessions
app.secret_key = 'changeme'

# 7️⃣ Route principale
@app.route('/', methods=['GET', 'POST'])
def index():
    form = SubscriptionForm()
    total = Subscription.query.count()

    if form.validate_on_submit():
        sub = Subscription(
            uuid=str(uuid.uuid4()),  # <-- génère un UUID unique à chaque fois
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

# 8️⃣ Export CSV
app.add_url_rule('/export', 'export_csv', export_csv)

# 9️⃣ Exécution locale
if __name__ == '__main__':
    app.run(debug=True)

