document.addEventListener('DOMContentLoaded', function() {
    var ticketMessage = document.getElementById('ticket-message');

    // Vérifier si l'utilisateur est connecté
    fetch('/check_login_status')
        .then(response => response.json())
        .then(data => {
            if (data.logged_in) {
                ticketMessage.innerHTML = "<p>Bienvenue!</p>";
            } else {
                ticketMessage.innerHTML = "<p>Pour acheter, veuillez vous connecter.</p>";
            }
        })
        .catch(error => {
            console.error('Une erreur s\'est produite:', error);
        });
});
