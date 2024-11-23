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
    const teammate = document.getElementById("teammate_username")?.value.trim();
    const player2Teammate = document.getElementById("player2_teammate")?.value.trim();
    const points = parseInt(document.getElementById("points").value, 10);
    const currentUser = "{{ user.username }}";

    // Validation contre soi-même
    if ([player2, teammate, player2Teammate].includes(currentUser)) {
        alert("Vous ne pouvez pas jouer contre vous-même.");
        return false;
    }

    // Validation des doublons
    const allPlayers = [player2, teammate, player2Teammate].filter(Boolean);
    const uniquePlayers = new Set(allPlayers);
    if (allPlayers.length !== uniquePlayers.size) {
        alert("Chaque pseudo doit être unique.");
        return false;
    }

    // Validation des points
    if (isNaN(points) || points <= 0 || points > 20) {
        alert("La différence de score doit être comprise entre 1 et 20.");
        return false;
    }

    return true;
}

function updateMatchForm() {
    const matchType = document.getElementById('match_type').value;
    const formFields = document.getElementById('form-fields');
    formFields.innerHTML = ''; // Réinitialise le contenu

    if (matchType === '1v1') {
        formFields.innerHTML = `
            <label for="player2_username">Pseudo de l'adversaire :</label>
            <input id="player2_username" name="player2_username" required>`;
    } else if (matchType === '1v2') {
        formFields.innerHTML = `
            <label for="player2_username">Pseudo de l'adversaire :</label>
            <input id="player2_username" name="player2_username" required>
            <label for="player2_teammate">Pseudo du coéquipier de l'adversaire :</label>
            <input id="player2_teammate" name="player2_teammate" required>`;
    } else if (matchType === '2v1') {
        formFields.innerHTML = `
            <label for="teammate_username">Pseudo de votre coéquipier :</label>
            <input id="teammate_username" name="teammate_username" required>
            <label for="player2_username">Pseudo de l'adversaire :</label>
            <input id="player2_username" name="player2_username" required>`;
    } else if (matchType === '2v2') {
        formFields.innerHTML = `
            <label for="teammate_username">Pseudo de votre coéquipier :</label>
            <input id="teammate_username" name="teammate_username" required>
            <label for="player2_username">Pseudo de l'adversaire :</label>
            <input id="player2_username" name="player2_username" required>
            <label for="player2_teammate">Pseudo du coéquipier de l'adversaire :</label>
            <input id="player2_teammate" name="player2_teammate" required>`;
    }
}

// Affiche le bouton lorsque l'utilisateur défile vers le bas
window.onscroll = function() {
    const backToTopButton = document.getElementById("back-to-top");
    if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
        backToTopButton.style.display = "block";
    } else {
        backToTopButton.style.display = "none";
    }
};

// Remonte en haut de la page quand le bouton est cliqué
document.getElementById("back-to-top").onclick = function() {
    window.scrollTo({ top: 0, behavior: "smooth" });
};
