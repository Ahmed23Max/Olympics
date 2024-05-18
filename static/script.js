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

// JavaScript pour basculer entre l'affichage du profil et du formulaire de modification
document.addEventListener("DOMContentLoaded", function () {
    const boutonEditerProfil = document.getElementById("editProfile");
    const boutonAnnulerModif = document.getElementById("cancelEdit");
    const boutonEnregistrerModif = document.getElementById("saveChanges");
    const formulaireProfil = document.getElementById("profileForm");
    const champDateNaissance = document.getElementById("date_of_birth");
    const selectPays = document.getElementById("country");
    const champNumeroTelephone = document.getElementById("phone_number");

    // Ajouter 27 pays supplémentaires avec leurs régions téléphoniques respectives
    const paysVersRegionTelephone = {
        "USA": "+1",
        "Canada": "+1",
        "Royaume-Uni": "+44",
        "Allemagne": "+49",
        "France": "+33",
        "Australie": "+61",
        "Japon": "+81",
        "Inde": "+91",
        "Brésil": "+55",
        "Mexique": "+52",
        "Chine": "+86",
        "Russie": "+7",
        "Corée du Sud": "+82",
        "Italie": "+39",
        "Espagne": "+34",
        "Pays-Bas": "+31",
        "Suède": "+46",
        "Norvège": "+47",
        "Danemark": "+45",
        "Finlande": "+358",
        "Suisse": "+41",
        "Autriche": "+43",
        "Belgique": "+32",
        "Grèce": "+30",
        "Portugal": "+351",
        "Irlande": "+353",
        "Nouvelle-Zélande": "+64",
    };

    boutonEditerProfil.addEventListener("click", function () {
        basculerFormulaireEdition();
    });

    boutonAnnulerModif.addEventListener("click", function () {
        basculerFormulaireEdition();
    });

    boutonEnregistrerModif.addEventListener("click", function () {
        // Sérialiser les données du formulaire en un objet JSON
        const donneesFormulaire = new FormData(formulaireProfil);
        const donnees = {};
        donneesFormulaire.forEach((value, key) => {
            donnees[key] = value;
        });

        // Vérifier si la date de naissance sélectionnée remonte à au moins 18 ans
        const dateNaissance = new Date(champDateNaissance.value);
        const maintenant = new Date();
        const age = maintenant.getFullYear() - dateNaissance.getFullYear();
        if (age < 18) {
            alert("Vous devez avoir au moins 18 ans pour mettre à jour votre profil.");
            return;
        }

        // Envoyer une requête AJAX pour mettre à jour les données du profil
        fetch("/mettre_a_jour_profil", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(donnees),
        })
            .then((response) => response.json())
            .then((resultat) => {
                if (resultat.message === "Profil mis à jour avec succès !") {
                    // Profil mis à jour avec succès, basculer le formulaire
                    basculerFormulaireEdition();
                } else {
                    // Gérer les erreurs ou afficher un message à l'utilisateur
                    console.error("Échec de la mise à jour du profil:", resultat.message);
                }
            })
            .catch((erreur) => {
                console.error("Une erreur s'est produite:", erreur);
            });
    });

    // Mettre à jour la région téléphonique en fonction du pays sélectionné
    selectPays.addEventListener("change", function () {
        const paysSelectionne = selectPays.value;
        const regionTelephone = paysVersRegionTelephone[paysSelectionne] || "";
        champNumeroTelephone.value = regionTelephone;
    });

    function basculerFormulaireEdition() {
        const carte = document.querySelector(".card");
        const formulaireEdition = document.getElementById("editForm");
        const boutonsEdition = document.getElementById("editButtons");

        if (carte.style.display === "none" || carte.style.display === "") {
            carte.style.display = "block";
            formulaireEdition.style.display = "none";
            boutonsEdition.style.display = "none";
        } else {
            carte.style.display = "none";
            formulaireEdition.style.display = "block";
            boutonsEdition.style.display = "block";
        }
    }
});
