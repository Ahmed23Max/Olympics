// Code JavaScript pour les fonctionnalités interactives (le cas échéant)
// Par exemple, validation des formulaires, interaction avec les éléments de la page, etc.
// Ce fichier peut être étendu avec d'autres fonctionnalités JavaScript en fonction des besoins du site.

// Exemple de validation de formulaire de contact
document.getElementById('contact-form').addEventListener('submit', function(event) {
    // Empêcher l'envoi par défaut du formulaire
    event.preventDefault();
    
    // Récupérer les valeurs des champs de formulaire
    var name = document.getElementById('name').value;
    var email = document.getElementById('email').value;
    var message = document.getElementById('message').value;
    
    // Validation des données
    if (name === '' || email === '' || message === '') {
        alert('Veuillez remplir tous les champs du formulaire.');
    } else {
        // Envoyer les données à un serveur (non implémenté dans cet exemple)
        alert('Votre message a été envoyé avec succès !');
    }
});
// Exemple de JavaScript pour une fonctionnalité de suivi d'événement
document.addEventListener('DOMContentLoaded', function() {
    // Enregistrement de l'événement de suivi
    trackEvent('Confirmation de Billet', 'Type', '{{ ticket_type }}');
});

// Fonction pour envoyer un événement de suivi à Google Analytics (exemple)
function trackEvent(category, action, label) {
    // Code pour envoyer l'événement de suivi à Google Analytics
    console.log('Tracking event:', category, action, label);
}
// Ouvrir le formulaire de demande de billet
function openTicketForm(ticketType) {
    var modal = document.getElementById('ticketFormModal');
    modal.style.display = 'block';
    // Vous pouvez utiliser ticketType pour personnaliser le formulaire en fonction du type de billet sélectionné
}

// Fermer le formulaire de demande de billet
function closeTicketForm() {
    var modal = document.getElementById('ticketFormModal');
    modal.style.display = 'none';
}

// Soumettre le formulaire de demande de billet
document.getElementById('ticketForm').addEventListener('submit', function(event) {
    event.preventDefault();
    // Traiter les données du formulaire ici
    var name = document.getElementById('name').value;
    var email = document.getElementById('email').value;
    // Vous pouvez ajouter d'autres champs et les traiter ici
    // Une fois le traitement terminé, vous pouvez fermer le formulaire
    closeTicketForm();
});

// Ouvrir le formulaire de connexion
function openLoginForm() {
    var modal = document.getElementById('loginModal');
    modal.style.display = 'block';
}

// Fermer le formulaire de connexion
function closeLoginForm() {
    var modal = document.getElementById('loginModal');
    modal.style.display = 'none';
}// Initialiser les composants Bootstrap

$(document).ready(function() {
    // Initialiser le dropdown
    $('.dropdown-toggle').dropdown();
});