from flask import request, jsonify, redirect, url_for, flash, session, render_template
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from donne import countries_with_flags
from flask import current_app

active_sessions = {}

def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        try:
            conn = psycopg2.connect(**current_app.config['db_config'])
            cursor = conn.cursor()

            cursor.execute("SELECT id, username, password, email FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user[2], password):
                session_id = str(uuid.uuid4())

                session['user_id'] = user[0]
                session['user_name'] = user[1]
                session['user_email'] = user[3]

                response = jsonify({"message": "Connexion réussie!"})
                response.set_cookie('session_id', session_id)
                return response
            else:
                return jsonify({"message": "Échec de la connexion. Veuillez vérifier vos informations d'identification."}), 401
        except psycopg2.Error as e:
            return jsonify({"message": "Une erreur s'est produite. Veuillez réessayer."}), 500
        finally:
            conn.close()

def signup():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        hashed_password = generate_password_hash(password, method='sha256')

        try:
            conn = psycopg2.connect(**current_app.config['db_config'])
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

def logout():
    session.clear()
    flash('Vous avez été déconnecté.', 'success')
    return redirect(url_for('index'))

def profile():
    if 'user_id' in session and 'user_name' in session:
        user_id = session['user_id']

        try:
            conn = psycopg2.connect(**current_app.config['db_config'])
            cursor = conn.cursor()

            cursor.execute("SELECT username, email, date_of_birth, location, phone_number FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            
            if user_data:
                user_name = user_data[0]
                user_email = user_data[1]
                user_date_of_birth = user_data[2] or 'Non fourni'
                user_location = user_data[3] or 'Non fourni'
                user_phone_number = user_data[4] or 'Non fourni'
            else:
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

def update_profile():
    if 'user_id' in session and 'user_name' in session:
        user_id = session['user_id']
        
        date_of_birth = request.form.get('date_of_birth')
        location = request.form.get('location')
        phone_number = request.form.get('phone_number')

        try:
            conn = psycopg2.connect(**current_app.config['db_config'])
            cursor = conn.cursor()

            cursor.execute("UPDATE users SET date_of_birth = %s, location = %s, phone_number = %s WHERE id = %s",
                           (date_of_birth, location, phone_number, user_id))

            conn.commit()

            session['user_date_of_birth'] = date_of_birth
            session['user_location'] = location
            session['user_phone_number'] = phone_number

            flash('Profil mis à jour avec succès!', 'success')
            return redirect(url_for('profile'))
        except psycopg2.Error as e:
            conn.rollback()
            flash('Échec de la mise à jour du profil. Veuillez réessayer.', 'danger')
            return redirect(url_for('profile'))  # Redirection en cas d'erreur
        finally:
            conn.close()

    return redirect(url_for('login'))
