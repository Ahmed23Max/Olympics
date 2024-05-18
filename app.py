from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash
import uuid



app = Flask(__name__)
app.secret_key = 'In9$]~3raxeG%L"7toNZwnuS:0D$?aq%{8+^R}(~<Xh3*P}.nmB4|fixQVwQ]:B'  # Clé secrète pour la sécurité des sessions

active_sessions = {}

# Your database configuration
db_config = {
    'dbname': 'olympics_ngoj',
    'user': 'olympics_ngoj_user',
    'password': 'XNB6TMo4a5VbkQ5X4DSgu1w03h63eP9F',
    'host': 'dpg-cp1p3p8l5elc73f2gat0-a.frankfurt-postgres.render.com'
}


# Route de connexion
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("SELECT id, username, password, email FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user[2], password):
                # Générer un identifiant de session unique
                session_id = str(uuid.uuid4())

                # Stocker les données de l'utilisateur dans le dictionnaire active_sessions
                active_sessions[session_id] = {
                    'user_id': user[0],
                    'user_name': user[1],
                    'user_email': user[3]  # Définir l'email de l'utilisateur dans la session
                }

                # Stocker l'identifiant, le nom et l'email de l'utilisateur dans la session
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                session['user_email'] = user[3]  # Définir l'email de l'utilisateur dans la session

                # Définir l'identifiant de session en tant que cookie
                response = jsonify({"message": "Connexion réussie!"})
                response.set_cookie('session_id', session_id)
                return response
            else:
                return jsonify({"message": "Échec de la connexion. Veuillez vérifier vos informations d'identification."}), 401
        except psycopg2.Error as e:
            return jsonify({"message": "Une erreur s'est produite. Veuillez réessayer."}), 500
        finally:
            conn.close()

# Route d'inscription
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Hacher le mot de passe avant de le stocker dans la base de données
        hashed_password = generate_password_hash(password, method='sha256')

        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                           (username, email, hashed_password))

            conn.commit()
            return jsonify({"message": "Inscription réussie! Vous pouvez maintenant vous connecter."}), 200
        except psycopg2.Error as e:
            conn.rollback()
            return jsonify({"message": "L'inscription a échoué. Veuillez réessayer."}), 400
        finally:
            conn.close()


@app.route('/logout')
def logout():
    session_id = request.cookies.get('session_id')
    if session_id:
        # Supprimer les données de session du dictionnaire active_sessions
        active_sessions.pop(session_id, None)

        # Effacer les données de session
        session.clear()

    flash('Vous avez été déconnecté.', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'user_id' in session and 'user_name' in session:
        user_id = session['user_id']

        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            # Récupérer les données de profil de l'utilisateur dans la base de données
            cursor.execute("SELECT username, email, date_of_birth, location, phone_number FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            
            if user_data:
                user_name = user_data[0]
                user_email = user_data[1]
                user_date_of_birth = user_data[2] or 'Non fourni'
                user_location = user_data[3] or 'Non fourni'
                user_phone_number = user_data[4] or 'Non fourni'
            else:
                # Gérer le cas où user_data est None
                user_name = session['user_name']
                user_email = session.get('user_email', 'Non fourni')
                user_date_of_birth = session.get('user_date_of_birth', 'Non fourni')
                user_location = session.get('user_location', 'Non fourni')
                user_phone_number = session.get('user_phone_number', 'Non fourni')

            return render_template('profile.html', user_name=user_name, user_email=user_email,
                                   user_date_of_birth=user_date_of_birth, user_location=user_location,
                                   user_phone_number=user_phone_number, countries_with_flags=countries_with_flags)
        except psycopg2.Error as e:
            flash('Une erreur s\'est produite lors de la récupération de votre profil. Veuillez réessayer.', 'danger')
            return redirect(url_for('login'))
        finally:
            conn.close()
    else:
        return redirect(url_for('login'))
    
    


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' in session and 'user_name' in session:
        user_id = session['user_id']
        
        # Obtenir les informations de profil à partir des données soumises du formulaire
        date_of_birth = request.form.get('date_of_birth')
        location = request.form.get('location')
        phone_number = request.form.get('phone_number')

        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            # Mettre à jour le profil de l'utilisateur dans la base de données
            cursor.execute("UPDATE users SET date_of_birth = %s, location = %s, phone_number = %s WHERE id = %s",
                           (date_of_birth, location, phone_number, user_id))

            conn.commit()

            # Mettre à jour les variables de session avec les nouvelles informations de profil
            session['user_date_of_birth'] = date_of_birth
            session['user_location'] = location
            session['user_phone_number'] = phone_number

            flash('Profil mis à jour avec succès!', 'success')
            return redirect(url_for('profile'))
        except psycopg2.Error as e:
            conn.rollback()
            flash('Échec de la mise à jour du profil. Veuillez réessayer.', 'danger')
            return redirect(url_for('profile'))
        finally:
            conn.close()
    else:
        return redirect(url_for('login'))


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



@app.route('/forgot_password')
def forgot_password():
    # Votre logique pour la réinitialisation du mot de passe
    return render_template('forgot_password.html')

# Add 27 more countries with flags to the dictionary
countries_with_flags = {
    "Albania": "🇦🇱",
    "Algeria": "🇩🇿",
    "Argentina": "🇦🇷",
    "Armenia": "🇦🇲",
    "Australia": "🇦🇺",
    "Bahamas": "🇧🇸",
    "Bahrain": "🇧🇭",
    "Bangladesh": "🇧🇩",
    "Barbados": "🇧🇧",
    "Belarus": "🇧🇾",
    "Belize": "🇧🇿",
    "Benin": "🇧🇯",
    "Bhutan": "🇧🇹",
    "Bolivia": "🇧🇴",
    "Brazil": "🇧🇷",
    "Brunei": "🇧🇳",
    "Bulgaria": "🇧🇬",
    "Cambodia": "🇰🇭",
    "Canada": "🇨🇦",
    "Cabo Verde": "🇨🇻",
    "Cameroon": "🇨🇲",
    "Chad": "🇹🇩",
    "Chile": "🇨🇱",
    "China": "🇨🇳",
    "Colombia": "🇨🇴",
    "Comoros": "🇰🇲",
    "Croatia": "🇭🇷",
    "Cyprus": "🇨🇾",
    "Côte d'Ivoire": "🇨🇮",
    "Djibouti": "🇩🇯",
    "Dominican Republic": "🇩🇴",
    "DR Congo": "🇨🇩",
    "Ecuador": "🇪🇨",
    "Egypt": "🇪🇬",
    "El Salvador": "🇸🇻",
    "Eritrea": "🇪🇷",
    "Estonia": "🇪🇪",
    "Eswatini": "🇸🇿",
    "Ethiopia": "🇪🇹",
    "Fiji": "🇫🇯",
    "Finland": "🇫🇮",
    "France": "🇫🇷",
    "Gambia": "🇬🇲",
    "Georgia": "🇬🇪",
    "Germany": "🇩🇪",
    "Ghana": "🇬🇭",
    "Grenada": "🇬🇩",
    "Guinea": "🇬🇳",
    "Guyana": "🇬🇾",
    "Haiti": "🇭🇹",
    "Honduras": "🇭🇳",
    "Hungary": "🇭🇺",
    "Iceland": "🇮🇸",
    "India": "🇮🇳",
    "Indonesia": "🇮🇩",
    "Iran": "🇮🇷",
    "Iraq": "🇮🇶",
    "Italy": "🇮🇹",
    "Jamaica": "🇯🇲",
    "Japan": "🇯🇵",
    "Jordan": "🇯🇴",
    "Kazakhstan": "🇰🇿",
    "Kenya": "🇰🇪",
    "Kuwait": "🇰🇼",
    "Kyrgyzstan": "🇰🇬",
    "Lao PDR": "🇱🇦",
    "Latvia": "🇱🇻",
    "Lebanon": "🇱🇧",
    "Liberia": "🇱🇷",
    "Libya": "🇱🇾",
    "Lithuania": "🇱🇹",
    "Luxembourg": "🇱🇺",
    "Macau": "🇲🇴",
    "Madagascar": "🇲🇬",
    "Malawi": "🇲🇼",
    "Maldives": "🇲🇻",
    "Mali": "🇲🇱",
    "Malta": "🇲🇹",
    "Mauritania": "🇲🇷",
    "Mauritius": "🇲🇺",
    "Mexico": "🇲🇽",
    "Moldova": "🇲🇩",
    "Mozambique": "🇲🇿",
    "Myanmar": "🇲🇲",
    "Namibia": "🇳🇦",
    "Nepal": "🇳🇵",
    "Netherlands": "🇳🇱",
    "New Zealand": "🇳🇿",
    "Nicaragua": "🇳🇮",
    "Niger": "🇳🇪",
    "Nigeria": "🇳🇬",
    "North Korea": "🇰🇵",
    "Norway": "🇳🇴",
    "Oman": "🇴🇲",
    "Pakistan": "🇵🇰",
    "Palestine": "🇵🇸",
    "Panama": "🇵🇦",
    "Peru": "🇵🇪",
    "Philippines": "🇵🇭",
    "Poland": "🇵🇱",
    "Portugal": "🇵🇹",
    "Qatar": "🇶🇦",
    "Rwanda": "🇷🇼",
    "Saint Lucia": "🇱🇨",
    "Saint Vincent and the Grenadines": "🇻🇨",
    "Samoa": "🇼🇸",
    "Saudi Arabia": "🇸🇦",
    "Senegal": "🇸🇳",
    "Sierra Leone": "🇸🇱",
    "Singapore": "🇸🇬",
    "Slovakia": "🇸🇰",
    "Slovenia": "🇸🇮",
    "Solomon Islands": "🇸🇧",
    "Somalia": "🇸🇴",
    "South Africa": "🇿🇦",
    "South Korea": "🇰🇷",
    "Spain": "🇪🇸",
    "Sri Lanka": "🇱🇰",
    "Sudan": "🇸🇩",
    "Suriname": "🇸🇷",
    "Sweden": "🇸🇪",
    "Switzerland": "🇨🇭",
    "Syria": "🇸🇾",
    "Taiwan": "🇹🇼",
    "Tajikistan": "🇹🇯",
    "Tanzania": "🇹🇿",
    "Timor-Leste": "🇹🇱",
    "Trinidad and Tobago": "🇹🇹",
    "Tunisia": "🇹🇳",
    "Turkey": "🇹🇷",
    "Uganda": "🇺🇬",
    "Ukraine": "🇺🇦",
    "United Arab Emirates": "🇦🇪",
    "United Kingdom": "🇬🇧",
    "United States": "🇺🇸",
    "Uruguay": "🇺🇾",
    "Uzbekistan": "🇺🇿",
    "Vanuatu": "🇻🇺",
    "Venezuela": "🇻🇪",
    "Vietnam": "🇻🇳",
    "Yemen": "🇾🇪",
    "Zimbabwe": "🇿🇼",
}

if __name__ == '__main__':
    app.run(debug=True)