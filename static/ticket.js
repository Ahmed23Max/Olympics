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
        });
    });
});