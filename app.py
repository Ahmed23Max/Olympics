import stripe
from flask import Flask, render_template, session, request, redirect, url_for, flash
from users import login, signup, logout, profile, update_profile
from config import db_config, STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY
from donne import disciplines
from config import SECRET_KEY
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = SECRET_KEY
stripe.api_key = STRIPE_SECRET_KEY

# Configuration de la base de données
app.config['db_config'] = db_config

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
        return render_template('ticket.html', tickets=tickets, logged_in=logged_in, stripe_public_key=STRIPE_PUBLIC_KEY)
    except psycopg2.Error as e:
        flash('Erreur lors de la récupération des billets.', 'danger')
        return render_template('ticket.html', tickets=[], logged_in='user_id' in session)
    finally:
        if conn:
            conn.close()

@app.route('/process_payment', methods=['POST'])
def process_payment():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour acheter un billet.', 'warning')
        return redirect(url_for('login'))

    ticket_id = request.form.get('ticket_id')
    quantity = int(request.form.get('quantity'))
    payment_method = request.form.get('payment_method')
    stripe_token = request.form.get('stripeToken') if payment_method == 'stripe' else None

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
        ticket = cursor.fetchone()
        available_tickets = ticket['available_tickets']
        price = ticket['price']

        if available_tickets >= quantity:
            amount = int(price * 100 * quantity)  # Stripe requires the amount in cents

            if payment_method == 'stripe':
                # Create a charge using Stripe
                charge = stripe.Charge.create(
                    amount=amount,
                    currency='eur',
                    source=stripe_token,
                    description=f"Achat de {quantity} billets pour {ticket['event_name']}"
                )
                charge_id = charge.id
            else:
                # Simulate a bank card payment process
                charge_id = 'bank_card_payment'

            # Insert the transaction into the database
            cursor.execute(
                "INSERT INTO transactions (user_id, ticket_id, quantity, stripe_charge_id) VALUES (%s, %s, %s, %s)",
                (session['user_id'], ticket_id, quantity, charge_id)
            )
            # Update the number of available tickets
            cursor.execute(
                "UPDATE tickets SET available_tickets = available_tickets - %s WHERE id = %s",
                (quantity, ticket_id)
            )

            conn.commit()
            flash('Billet(s) acheté(s) avec succès!', 'success')
        else:
            flash('Quantité de billets insuffisante.', 'danger')
    except stripe.error.StripeError as e:
        flash(f"Erreur Stripe: {str(e)}", 'danger')
    except psycopg2.Error as e:
        conn.rollback()
        flash('Erreur lors de l\'achat du billet.', 'danger')
    finally:
        if conn:
            conn.close()
        return redirect(url_for('tickets'))

if __name__ == '__main__':
    app.run(debug=True)
