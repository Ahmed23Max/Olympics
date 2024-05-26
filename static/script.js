document.addEventListener("DOMContentLoaded", function () {
    const togglePasswordButtons = document.querySelectorAll('.btn-toggle-password');

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

    // Ajoutez ici le code spécifique à d'autres fonctionnalités de votre application
});
