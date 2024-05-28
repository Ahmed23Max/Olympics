import unittest
from unittest.mock import patch
from app import app
import psycopg2

class TestApp(unittest.TestCase):

    def setUp(self):
        # Créer un client de test pour interagir avec l'application
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_events(self):
        response = self.app.get('/events')
        self.assertEqual(response.status_code, 200)

    def test_discipline_details(self):
        response = self.app.get('/discipline/1')
        self.assertEqual(response.status_code, 200)

        # Test avec un ID de discipline invalide
        response = self.app.get('/discipline/1000')
        self.assertEqual(response.status_code, 404)

    def test_practical_info(self):
        response = self.app.get('/practical-info')
        self.assertEqual(response.status_code, 200)

    def test_sitemap(self):
        response = self.app.get('/sitemap')
        self.assertEqual(response.status_code, 200)

    def test_tickets(self):
        response = self.app.get('/tickets')
        self.assertEqual(response.status_code, 200)

    def test_process_purchase(self):
        # Test d'achat réussi
        response = self.app.post('/process_purchase', json={
            'ticket_id': 1,
            'event_name': 'Event Name',
            'event_date': '2024-05-28',
            'price': '10.00',
            'quantity': 1,
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'phone': '123456789',
            'address': '123 Street',
            'city': 'City',
            'postal_code': '12345'
        })
        self.assertEqual(response.status_code, 200)

        # Test d'achat échoué avec des données manquantes
        response = self.app.post('/process_purchase', json={})
        self.assertEqual(response.status_code, 500)

    def test_success(self):
        response = self.app.get('/success')
        self.assertEqual(response.status_code, 200)

    def test_cancel(self):
        response = self.app.get('/cancel')
        self.assertEqual(response.status_code, 302)  # Redirection

    def test_login(self):
        # Test de connexion réussie
        response = self.app.post('/login', json={
            'username': 'Amino',
            'password': 'amino1998'
        })
        self.assertEqual(response.status_code, 200)

        # Test de connexion échouée avec mauvais mot de passe
        response = self.app.post('/login', json={
            'username': 'test_user',
            'password': 'wrong_password'
        })
        self.assertEqual(response.status_code, 401)

        # Test de connexion échouée avec utilisateur inexistant
        response = self.app.post('/login', json={
            'username': 'non_existing_user',
            'password': 'test_password'
        })
        self.assertEqual(response.status_code, 401)

    def test_signup(self):
        # Test d'inscription réussie
        response = self.app.post('/signup', json={
            'username': 'new_user',
            'email': 'new_user@example.com',
            'password': 'password',
            'confirm_password': 'password'
        })
        self.assertEqual(response.status_code, 200)

        # Test d'inscription échouée avec mots de passe non correspondants
        response = self.app.post('/signup', json={
            'username': 'new_user',
            'email': 'new_user@example.com',
            'password': 'password',
            'confirm_password': 'different_password'
        })
        self.assertEqual(response.status_code, 400)

        # Test d'inscription échouée avec nom d'utilisateur déjà existant
        response = self.app.post('/signup', json={
            'username': 'existing_user',
            'email': 'new_user@example.com',
            'password': 'password',
            'confirm_password': 'password'
        })
        self.assertEqual(response.status_code, 400)

        # Test d'inscription échouée avec e-mail déjà existant
        response = self.app.post('/signup', json={
            'username': 'new_user',
            'email': 'existing_user@example.com',
            'password': 'password',
            'confirm_password': 'password'
        })
        self.assertEqual(response.status_code, 400)

    def test_logout(self):
        response = self.app.get('/logout')
        self.assertEqual(response.status_code, 302)  # Redirection

    def test_profile(self):
        response = self.app.get('/profile')
        self.assertEqual(response.status_code, 302)  # Redirection

    def test_update_profile(self):
        response = self.app.post('/update_profile')
        self.assertEqual(response.status_code, 302)  # Redirection


if __name__ == '__main__':
    unittest.main()
