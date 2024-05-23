document.addEventListener('DOMContentLoaded', function() {
    var purchaseModal = $('#purchaseModal');
    purchaseModal.on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var ticketId = button.data('ticket-id');
        var eventName = button.data('event-name');
        var eventDate = button.data('event-date');
        var price = button.data('price');
        var availableTickets = button.data('available-tickets'); // Ajout de cette ligne
        var eventId = button.data('event-id');

        var modal = $(this);
        modal.find('#modal-ticket-id').val(ticketId);
        modal.find('#modal-event-name').text(eventName);
        modal.find('#modal-event-date').text(eventDate);
        modal.find('#modal-price').text(price);
        modal.find('#modal-available-tickets').text(availableTickets); // Ajout de cette ligne
        modal.find('#modal-quantity').attr('max', availableTickets);

        // Set hidden fields with ticket and event details
        modal.find('#modal-event-name-input').val(eventName);
        modal.find('#modal-event-date-input').val(eventDate);
        modal.find('#modal-price-input').val(price);
        modal.find('#modal-event-id-input').val(eventId);
    });

    // Ajouter un événement 'click' à chaque bouton 'Acheter'
    $('.btn-primary').click(function(event) {
        var button = $(this);
        var ticketId = button.data('ticket-id');
        var eventName = button.data('event-name');
        var eventDate = button.data('event-date');
        var price = button.data('price');
        var availableTickets = button.data('available-tickets'); // Ajout de cette ligne

        var modal = $('#purchaseModal');
        modal.find('#modal-event-name').text(eventName);
        modal.find('#modal-event-date').text(eventDate);
        modal.find('#modal-price').text(price);
        modal.find('#modal-available-tickets').text(availableTickets); // Ajout de cette ligne
    });

    var stripe = Stripe(stripePublicKey);
    var elements = stripe.elements();
    var card = elements.create('card');
    card.mount('#stripe-card-element');

    var form = document.getElementById('purchase-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        stripe.createToken(card).then(function(result) {
            if (result.error) {
                // Inform the user if there was an error.
                console.log(result.error.message);
            } else {
                // Send the token to your server.
                var hiddenInput = document.createElement('input');
                hiddenInput.setAttribute('type', 'hidden');
                hiddenInput.setAttribute('name', 'stripeToken');
                hiddenInput.setAttribute('value', result.token.id);
                form.appendChild(hiddenInput);
                form.submit();
            }
        });
    });
});

