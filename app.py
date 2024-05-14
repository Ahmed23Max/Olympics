from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '4249E775DF4E1E51A94FC83A1FB55'  # Clé secrète pour la sécurité des sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://olympics_ngoj_user:XNB6TMo4a5VbkQ5X4DSgu1w03h63eP9F@dpg-cp1p3p8l5elc73f2gat0-a/olympics_ngoj'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Option recommandée pour améliorer les performances

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Modèle de données pour les utilisateurs
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

# Formulaire d'inscription
class RegistrationForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('S\'inscrire')

# Formulaire de connexion
class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')

# Routes
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Définition des disciplines sportives avec leurs logos et descriptions
disciplines = [
    {"name": "Athlétisme", "logo": "logo/athletics.jpg", "description": "Ne manquez pas les compétitions d'athlétisme mettant en vedette les meilleurs athlètes du monde."},
    {"name": "Aviron", "logo": "logo/rowing.jpg", "description": "Assistez aux épreuves d'aviron et soutenez votre équipe préférée."},
    {"name": "Badminton", "logo": "logo/badminton.jpg", "description": "Regardez les matchs de badminton où les joueurs se battent pour la médaille d'or."},
    {"name": "Basket-ball à 5", "logo": "logo/basketball.jpg", "description": "Suivez les rencontres passionnantes de basket-ball à 5."},
    {"name": "Basket 3x3", "logo": "logo/basketball.jpg", "description": "Découvrez l'intensité du basket 3x3 où chaque panier compte."},
    {"name": "Boxe", "logo": "logo/boxing.jpg", "description": "Assistez aux combats de boxe et vibrez avec chaque coup de poing."},
    {"name": "Breakdance", "logo": "logo/breakdance.jpg", "description": "Plongez dans l'univers dynamique du breakdance, la nouvelle discipline olympique."},
    {"name": "Canoë-Kayak Course en Ligne", "logo": "logo/canoe.jpg", "description": "Suivez les courses passionnantes de canoë-kayak en ligne."},
    {"name": "Canoë-Kayak Slalom", "logo": "logo/canoe.jpg", "description": "Vivez l'adrénaline des courses de canoë-kayak en slalom."},
    {"name": "BMX", "logo": "logo/bmx.jpg", "description": "Regardez les compétitions de BMX et admirez les prouesses des coureurs."},
    {"name": "VTT", "logo": "logo/mtb.jpg", "description": "Explorez les pistes de VTT et assistez aux courses pleines de suspense."},
    {"name": "Cyclisme sur Piste", "logo": "logo/track_cycling.jpg", "description": "Suivez les courses de cyclisme sur piste et ressentez la vitesse."},
    {"name": "Cyclisme sur Route", "logo": "logo/road_cycling.jpg", "description": "Parcourez les routes avec les cyclistes lors des courses sur route."},
    {"name": "Équitation", "logo": "logo/equestrian.jpg", "description": "Voyez les cavaliers et leurs chevaux en action lors des épreuves d'équitation."},
    {"name": "Escalade", "logo": "logo/climbing.jpg", "description": "Assistez aux compétitions d'escalade et vivez la montée d'adrénaline."},
    {"name": "Escrime", "logo": "logo/fencing.jpg", "description": "Regardez les duels passionnants des escrimeurs pour décrocher l'or."},
    {"name": "Football", "logo": "logo/football.jpg", "description": "Suivez les matchs de football et encouragez votre équipe préférée."},
    {"name": "Golf", "logo": "logo/golf.jpg", "description": "Suivez les joueurs de golf sur le parcours et profitez des moments de suspense."},
    {"name": "Gymnastique Artistique", "logo": "logo/gymnastics.jpg", "description": "Admirez les performances spectaculaires des gymnastes artistiques."},
    {"name": "Gymnastique Rythmique", "logo": "logo/rhythmic_gymnastics.jpg", "description": "Sentez la grâce des gymnastes lors des épreuves de gymnastique rythmique."},
    {"name": "Trampoline", "logo": "logo/trampoline.jpg", "description": "Vivez les moments palpitants des épreuves de trampoline."},
    {"name": "Haltérophilie", "logo": "logo/weightlifting.jpg", "description": "Assistez aux compétitions d'haltérophilie et admirez la force des athlètes."},
    {"name": "Handball", "logo": "logo/handball.jpg", "description": "Vivez l'action frénétique des matchs de handball."},
    {"name": "Hockey sur Gazon", "logo": "logo/hockey.jpg", "description": "Suivez les matchs de hockey sur gazon et ressentez l'intensité du jeu."},
    {"name": "Judo", "logo": "logo/judo.jpg", "description": "Regardez les combats de judo et découvrez la discipline et la grâce des judokas."},
    {"name": "Lutte", "logo": "logo/wrestling.jpg", "description": "Assistez aux combats de lutte et ressentez la tension sur le tapis."},
    {"name": "Natation", "logo": "logo/swimming.jpg", "description": "Plongez dans l'action des courses de natation et encouragez vos nageurs préférés."},
    {"name": "Natation Artistique", "logo": "logo/artistic_swimming.jpg", "description": "Admirez la synchronisation et l'élégance des nageuses en natation artistique."},
    {"name": "Plongeon", "logo": "logo/diving.jpg", "description": "Regardez les plongeurs défier la gravité et réaliser des sauts époustouflants."},
    {"name": "Water-Polo", "logo": "logo/water_polo.jpg", "description": "Suivez les matchs passionnants de water-polo et ressentez l'excitation du jeu."},
    {"name": "Pentathlon Moderne", "logo": "logo/modern_pentathlon.jpg", "description": "Vivez l'action du pentathlon moderne, une combinaison d'épreuves sportives."},
    {"name": "Rugby à 7", "logo": "logo/rugby.jpg", "description": "Regardez les équipes s'affronter lors des matchs de rugby à 7."},
    {"name": "Skateboard", "logo": "logo/skateboarding.jpg", "description": "Découvrez les prouesses des skateurs lors des épreuves de skateboard."},
    {"name": "Surf", "logo": "logo/surfing.jpg", "description": "Plongez dans l'océan et admirez les surfeurs dompter les vagues."},
    {"name": "Taekwondo", "logo": "logo/taekwondo.jpg", "description": "Assistez aux combats de taekwondo et ressentez l'intensité des coups de pied."},
    {"name": "Tennis", "logo": "logo/tennis.jpg", "description": "Regardez les échanges rapides et passionnants lors des matchs de tennis."},
    {"name": "Tennis de Table", "logo": "logo/table_tennis.jpg", "description": "Suivez les matchs de tennis de table et admirez la vitesse et la précision des joueurs."},
    {"name": "Tir", "logo": "logo/shooting.jpg", "description": "Voyez la concentration des tireurs lors des épreuves de tir."},
    {"name": "Tir à l'Arc", "logo": "logo/archery.jpg", "description": "Regardez les archers viser avec précision lors des épreuves de tir à l'arc."},
    {"name": "Triathlon", "logo": "logo/triathlon.jpg", "description": "Suivez les athlètes dans leur parcours éprouvant lors des épreuves de triathlon."},
    {"name": "Voile", "logo": "logo/sailing.jpg", "description": "Explorez les mers et admirez les voiliers lors des compétitions de voile."},
    {"name": "Beach-Volley", "logo": "logo/beach_volleyball.jpg", "description": "Vivez l'ambiance estivale et les matchs énergiques de beach-volley."},
    {"name": "Volley-ball", "logo": "logo/volleyball.jpg", "description": "Suivez les matchs passionnants de volley-ball et ressentez l'excitation du jeu."},
]

@app.route('/events')
def events():
    return render_template('events.html', disciplines=disciplines)

@app.route('/discipline/<int:discipline_id>')
def discipline_details(discipline_id):
    # Récupérer les détails de la discipline à partir de l'ID
    discipline = disciplines[discipline_id]
    return render_template('discipline_details.html', discipline=discipline)

@app.route('/practical-info')
def practical_info():
    return render_template('practical-info.html')

@app.route('/sitemap')
def sitemap():
    return render_template('sitemap.html')

# Route pour le formulaire d'inscription
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Sauvegarde des détails de l'utilisateur dans la base de données
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Votre compte a été créé avec succès !', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Inscription', form=form)

# Route pour le formulaire de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Récupérer l'utilisateur depuis la base de données en fonction du nom d'utilisateur
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Connexion réussie
            return redirect(url_for('index'))
        else:
            flash('Échec de la connexion. Veuillez vérifier votre nom d\'utilisateur et votre mot de passe.', 'danger')
    return render_template('login.html', title='Connexion', form=form)

@app.route('/tickets', methods=['GET', 'POST'])
def tickets():
    if request.method == 'POST':
        ticket_type = request.form['ticket-type']
        # Vous pouvez ajouter ici le traitement du type de billet sélectionné
        # Par exemple, rediriger vers une page de confirmation de billet
        return redirect(url_for('ticket_confirmation', ticket_type=ticket_type))
    return render_template('tickets.html')

@app.route('/ticket-confirmation/<ticket_type>')
def ticket_confirmation(ticket_type):
    # Vous pouvez utiliser le type de billet ici pour afficher une confirmation personnalisée
    return render_template('ticket_confirmation.html', ticket_type=ticket_type)

@app.route('/user-space')
def user_space():
    return render_template('user-space.html')

@app.route('/forgot_password')
def forgot_password():
    # Votre logique pour la réinitialisation du mot de passe
    return render_template('forgot_password.html')

if __name__ == '__main__':
    app.run(debug=True)