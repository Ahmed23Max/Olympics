// ticket.js

document.addEventListener('DOMContentLoaded', function() {
    const purchaseForms = document.querySelectorAll('.purchase-form');

    purchaseForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(form);

            fetch('/purchase_ticket', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Billet acheté avec succès!');
                    location.reload(); // Recharger la page pour mettre à jour les données
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Erreur lors de l\'achat du billet:', error);
                alert('Une erreur s\'est produite lors de l\'achat du billet. Veuillez réessayer.');
            });
        });
    });
});
