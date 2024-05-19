from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from config import db_config, SECRET_KEY
from donne import disciplines, countries_with_flags

app = Flask(__name__)
app.secret_key = SECRET_KEY

active_sessions = {}


unique_key = uuid.uuid4().hex

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

# Route pour afficher la page des billets
@app.route('/tickets')
def tickets():
    return render_template('ticket.html')

# Route pour vérifier l'état de connexion
@app.route('/check_login_status')
def check_login_status():
    if 'user_id' in session:
        return jsonify({'logged_in': True})
    else:
        return jsonify({'logged_in': False})


if __name__ == '__main__':
    app.run(debug=True)