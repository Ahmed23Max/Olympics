// Sélectionner les éléments de connexion et d'inscription
const loginButton = document.getElementById('login-button');
const signupButton = document.getElementById('signup-button');
const loginForm = document.getElementById('login-form');
const signupForm = document.getElementById('signup-form');
const togglePasswordButtons = document.querySelectorAll('.btn-toggle-password');

// Écouteur d'événements pour le bouton de connexion
loginButton.addEventListener('click', () => {
    loginForm.style.display = 'block';
    signupForm.style.display = 'none';
});

// Écouteur d'événements pour le bouton d'inscription
signupButton.addEventListener('click', () => {
    signupForm.style.display = 'block';
    loginForm.style.display = 'none';
});

// Fonction pour basculer la visibilité du mot de passe
function togglePasswordVisibility(inputElement, toggleButton) {
    const passwordInput = inputElement;
    const eyeIcon = toggleButton.querySelector('i');
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        eyeIcon.classList.remove('bi-eye-slash');
        eyeIcon.classList.add('bi-eye');
    } else {
        passwordInput.type = 'password';
        eyeIcon.classList.remove('bi-eye');
        eyeIcon.classList.add('bi-eye-slash');
    }
}

// Écouteur d'événements pour les boutons "Afficher le mot de passe"
togglePasswordButtons.forEach((button) => {
    button.addEventListener('click', () => {
        const passwordInput = button.parentElement.parentElement.querySelector('input[type="password"]');
        togglePasswordVisibility(passwordInput, button);
    });
});

// Écouteur d'événements pour la soumission du formulaire d'inscription
signupForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const signupUsername = document.getElementById('signup-username').value;
    const signupEmail = document.getElementById('signup-email').value;
    const signupPassword = document.getElementById('signup-password').value;
    const signupConfirmPassword = document.getElementById('signup-confirm-password').value;

    if (signupPassword !== signupConfirmPassword) {
        alert('Le mot de passe et la confirmation du mot de passe doivent correspondre.');
        return;
    }

    try {
        const response = await fetch("/signup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username: signupUsername,
                email: signupEmail,
                password: signupPassword,
            }),
        });

        if (response.ok) {
            alert('Inscription réussie ! Vous pouvez maintenant vous connecter.');
            loginForm.style.display = 'block'; // Afficher le formulaire de connexion après une inscription réussie
            signupForm.style.display = 'none'; // Masquer le formulaire d'inscription
            // Optionnellement, vous pouvez effacer les champs du formulaire d'inscription ici
        } else {
            alert("L'inscription a échoué. Veuillez réessayer.");
        }
    } catch (error) {
        console.error(error);
        alert('Une erreur s\'est produite. Veuillez réessayer.');
    }
});

// Écouteur d'événements pour la soumission du formulaire de connexion
loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const loginUsername = document.getElementById('login-username').value;
    const loginPassword = document.getElementById('login-password').value;

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username: loginUsername,
                password: loginPassword,
            }),
        });

        if (response.ok) {
            alert('Connexion réussie !');
            // Recharger la page après une connexion réussie
            window.location.reload();
        } else {
            alert('La connexion a échoué. Veuillez réessayer.');
        }
    } catch (error) {
        console.error(error);
        alert('Une erreur s\'est produite. Veuillez réessayer.');
    }
});

// Sélectionner le bouton de modification
const editProfileButton = document.getElementById('editProfileButton');
const editForm = document.getElementById('editForm');

// Écouteur d'événements pour le bouton de modification
editProfileButton.addEventListener('click', () => {
    // Basculer le style d'affichage de l'élément editForm
    if (editForm.style.display === 'none' || editForm.style.display === '') {
        editForm.style.display = 'block';
    } else {
        editForm.style.display = 'none';
    }
});
