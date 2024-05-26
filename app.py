from flask import Flask, render_template, session, request, jsonify, flash, redirect, url_for
from users import login, signup, logout, profile, update_profile
from config import db_config, SECRET_KEY, STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY
from donne import disciplines
import stripe
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Configuration de la base de données
app.config['db_config'] = db_config

# Configuration de Stripe
stripe.api_key = STRIPE_SECRET_KEY

# Route de connexion
app.add_url_rule('/login', 'login', login, methods=['POST'])

# Route d'inscription
app.add_url_rule('/signup', 'signup', signup, methods=['POST'])

# Route de déconnexion
app.add_url_rule('/logout', 'logout', logout)

# Route de profil
app.add_url_rule('/profile', 'profile', profile)

# Route de mise à jour de profil
app.add_url_rule('/update_profile', 'update_profile', update_profile, methods=['POST'])

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

@app.route('/tickets')
def tickets():
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM tickets")
        tickets = cursor.fetchall()
        logged_in = 'user_id' in session
        return render_template('ticket.html', tickets=tickets, logged_in=logged_in, stripe_publishable_key=STRIPE_PUBLISHABLE_KEY)
    except psycopg2.Error as e:
        flash('Erreur lors de la récupération des billets.', 'danger')
        return render_template('ticket.html', tickets=[], logged_in='user_id' in session)
    finally:
        if conn:
            conn.close()

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

@app.route('/process_purchase', methods=['POST'])
def process_purchase():
    ticket_id = request.form['ticket_id']
    event_name = request.form['event_name']
    event_date = request.form['event_date']
    price = request.form['price']

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': event_name,
                    },
                    'unit_amount': int(float(price) * 100),  # Stripe expects amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('success', _external=True),
            cancel_url=url_for('cancel', _external=True),
        )
        return redirect(session.url, code=303)
    except Exception as e:
        flash('Erreur lors de la création de la session de paiement.', 'danger')
        return redirect(url_for('tickets'))

if __name__ == '__main__':
    app.run(debug=True)
