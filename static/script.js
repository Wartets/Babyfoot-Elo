document.addEventListener('DOMContentLoaded', function () {
    const title = document.querySelector('header h1');
    const letters = title.innerText.split('');
    title.innerHTML = '';
    letters.forEach(letter => {
        const span = document.createElement('span');
        span.innerText = letter;
        title.appendChild(span);
    });
});

// Validation de la confirmation de mot de passe
document.querySelector("form").addEventListener("submit", function (e) {
	const password = document.getElementById("password").value;
	const confirmPassword = document.getElementById("confirm_password").value;
	
	if (password !== confirmPassword) {
		e.preventDefault(); // Empêcher l'envoi du formulaire
		alert("Les mots de passe ne correspondent pas !");
	}
});

function validateMatchForm() {
	const player2 = document.getElementById("player2_username").value.trim();
	const points = parseInt(document.getElementById("points").value, 10);
	const currentUser = "{{ user.username }}";  // Récupérer le pseudo de l'utilisateur connecté

	if (player2 === currentUser) {
		alert("Vous ne pouvez pas jouer contre vous-même.");
		return false;
	}

	if (isNaN(points) || points <= 0 || points > 100) {
		alert("La différence de score doit être comprise entre 1 et 100.");
		return false;
	}

	return true;
}