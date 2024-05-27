from flask import Flask, render_template, session, request, flash, redirect, url_for, jsonify
import stripe
import psycopg2
import psycopg2.extras
from donne import disciplines
from users import login, signup, logout, profile, update_profile
from config import db_config, SECRET_KEY, STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY
import qrcode
import os
import logging
from unidecode import unidecode

app = Flask(__name__)
app.secret_key = SECRET_KEY
# Configuration du logging
logging.basicConfig(filename='qr_code.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
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
        full_name = data.get('full_name')
        email = data.get('email')
        phone = data.get('phone')
        address = data.get('address')
        city = data.get('city')
        postal_code = data.get('postal_code')

        # Mettre à jour le nombre de tickets disponibles dans la base de données
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Mettre à jour le nombre de tickets disponibles dans la base de données
        cursor.execute("UPDATE tickets SET available_tickets = available_tickets - %s WHERE id = %s", (quantity, ticket_id))
        conn.commit()

        # Enregistrer une trace de l'achat dans la base de données
        user_id = session.get('user_id', None)  # Assurez-vous que l'utilisateur est connecté
        if user_id:
            cursor.execute("INSERT INTO purchases (user_id, ticket_id, quantity, price, full_name, email, phone, address, city, postal_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (user_id, ticket_id, quantity, price, full_name, email, phone, address, city, postal_code))
            conn.commit()

        cursor.close()
        conn.close()

        stripe_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': event_name,
                    },
                    'unit_amount': int(float(price) * 100),
                },
                'quantity': int(quantity),
            }],
            mode='payment',
            success_url=url_for('success', 
                                event_name=event_name, 
                                event_date=event_date, 
                                price=price, 
                                quantity=quantity, 
                                full_name=full_name, 
                                email=email, 
                                phone=phone, 
                                address=address, 
                                city=city, 
                                postal_code=postal_code, 
                                _external=True),
            cancel_url=url_for('cancel', _external=True)
        )

        return jsonify({'url': stripe_session.url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/success')
def success():
    # Récupérer les informations du ticket depuis la requête
    event_name = request.args.get('event_name')
    event_date = request.args.get('event_date')
    price = request.args.get('price')
    quantity = request.args.get('quantity')
    full_name = request.args.get('full_name')
    email = request.args.get('email')
    phone = request.args.get('phone')
    address = request.args.get('address')
    city = request.args.get('city')
    postal_code = request.args.get('postal_code')

    # Générer le contenu du ticket avec les informations nécessaires
    ticket_info = f"Event: {event_name}\nDate: {event_date}\nPrice: {price}\nQuantity: {quantity}\nName: {full_name}\nEmail: {email}\nPhone: {phone}\nAddress: {address}\nCity: {city}\nPostal Code: {postal_code}"

    # Générer et sauvegarder le QR code
    qr_code_path = generate_qr_code(ticket_info)

    return render_template('success.html', event_name=event_name, event_date=event_date, price=price, quantity=quantity, full_name=full_name, email=email, phone=phone, address=address, city=city, postal_code=postal_code, qr_code_path=qr_code_path)



def generate_qr_code(ticket_info):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(ticket_info)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # Créer le répertoire s'il n'existe pas
        directory = 'static/qrcodes'
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Translittérer les caractères spéciaux en ASCII standard
        filename = unidecode(ticket_info)
        
        # Remplacer les caractères spéciaux et les tirets bas par des tirets
        filename = filename.replace(' ', '_').replace(':', '-').replace('.', '-')
        
        img_path = os.path.join(directory, f"{filename}.png")  # Utilisez os.path.join pour créer le chemin absolu
        img.save(img_path)
        logging.info(f"QR code généré avec succès : {img_path}")
        return img_path
    except Exception as e:
        logging.error(f"Erreur lors de la génération du QR code : {e}")
        raise




@app.route('/cancel')
def cancel():
    flash('Le paiement a été annulé.', 'info')
    return redirect(url_for('tickets'))

if __name__ == '__main__':
    app.run(debug=True)
