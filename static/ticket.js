document.addEventListener('DOMContentLoaded', (event) => {
    var purchaseButtons = document.querySelectorAll('.purchase-button');
    purchaseButtons.forEach((button) => {
        button.addEventListener('click', (event) => {
            var ticketId = event.target.getAttribute('data-ticket-id');
            var eventName = event.target.getAttribute('data-event-name');
            var eventDate = event.target.getAttribute('data-event-date');
            var price = event.target.getAttribute('data-price');

            document.getElementById('ticket_id').value = ticketId;
            document.getElementById('event_name').value = eventName;
            document.getElementById('event_date').value = eventDate;
            document.getElementById('price').value = price;
            document.getElementById('quantity').value = 1;  // Valeur par défaut de la quantité à 1
        });
    });

    var purchaseForm = document.getElementById('purchaseForm');
    purchaseForm.addEventListener('submit', (event) => {
        // La quantité est déjà incluse dans le formulaire

        // Empêcher l'envoi par défaut du formulaire
        event.preventDefault();

        // Récupérer les données du formulaire
        var formData = new FormData(purchaseForm);
        var ticketId = formData.get('ticket_id');
        var eventName = formData.get('event_name');
        var eventDate = formData.get('event_date');
        var price = formData.get('price');
        var quantity = formData.get('quantity');

        // Créer une nouvelle session de paiement Stripe
        fetch('/process_purchase', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ticket_id: ticketId,
                event_name: eventName,
                event_date: eventDate,
                price: price,
                quantity: quantity
            }),
        })
        .then(response => response.json())
        .then(data => {
            // Rediriger vers la page de paiement Stripe
            window.location.href = data.url;
        })
        .catch(error => {
            // Gérer l'erreur
            console.error('Erreur lors de la création de la session de paiement:', error);
        });
    });
});
