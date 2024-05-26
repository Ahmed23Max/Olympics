from flask import Flask, render_template, session, request, flash, redirect, url_for, jsonify
from users import login, signup, logout, profile, update_profile
from config import db_config, SECRET_KEY, STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY
import stripe
import psycopg2
import psycopg2.extras
from donne import disciplines
from datetime import datetime

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

@app.route('/process_purchase', methods=['POST'])
def process_purchase():
    try:
        data = request.json
        ticket_id = data.get('ticket_id')
        event_name = data.get('event_name')
        event_date = data.get('event_date')
        price = data.get('price')
        quantity = data.get('quantity')

        # Créer une nouvelle session de paiement Stripe
        stripe_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': event_name,
                    },
                    'unit_amount': int(float(price) * 100),  # Stripe attend le montant en cents
                },
                'quantity': int(quantity),  # Utiliser la quantité de tickets
            }],
            mode='payment',
            success_url=url_for('success', _external=True, session_id='{CHECKOUT_SESSION_ID}'),
            cancel_url=url_for('cancel', _external=True),
            metadata={
                'ticket_id': ticket_id,
                'user_id': session.get('user_id')
            }
        )

        # Mettre à jour le nombre de tickets disponibles et enregistrer la transaction
        try:
            ticket_id = int(stripe_session.metadata['ticket_id'])  # Convertir en entier
            quantity = int(stripe_session.metadata['quantity'])    # Convertir en entier
            event_name = stripe_session.metadata['event_name']     # Récupérer le nom de l'événement

            # Mettre à jour le nombre de tickets disponibles
            update_ticket_availability(ticket_id, quantity)

            # Enregistrer les détails de la transaction
            record_transaction(stripe_session.id, ticket_id, quantity, event_name)

            flash('Votre achat a été réalisé avec succès.', 'success')
        except Exception as e:
            flash('Erreur lors de l\'enregistrement de la transaction: {}'.format(str(e)), 'danger')

        return jsonify({'url': stripe_session.url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route de succès après un paiement Stripe réussi
@app.route('/success')
def success():
    session_id = request.args.get('session_id')
    return redirect(url_for('tickets'))

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

# Fonction pour mettre à jour le nombre de tickets disponibles dans la base de données
def update_ticket_availability(ticket_id, quantity):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tickets SET available_tickets = available_tickets - %s WHERE id = %s",
            (quantity, ticket_id)
        )
        conn.commit()
    finally:
        if conn:
            conn.close()

# Fonction pour enregistrer les détails de la transaction dans la base de données
def record_transaction(session_id, ticket_id, quantity, event_name):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transactions (session_id, ticket_id, quantity, event_name, transaction_date) VALUES (%s, %s, %s, %s, %s)",
            (session_id, ticket_id, quantity, event_name, datetime.now())
        )
        conn.commit()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
