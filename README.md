# Babyfoot Elo - Système de Classement ELO

Ce projet est une application web pour gérer les classements ELO des joueurs de babyfoot. Voici comment l'utiliser en local.

## Prérequis

- Python 3.x installé
- SQLite (inclus avec Python)
- Navigateur web

## Installation et configuration

1. **Clonez ce dépôt**
   ```bash
   git clone https://github.com/wartets/babyfoot-elo.git
   cd babyfoot-elo
   ```

2. **Installez les dépendances nécessaires**
   Installez Flask et les autres dépendances nécessaires à l'application en utilisant la commande suivante :
   ```bash
   pip install flask flask-sqlalchemy werkzeug
   ```

3. **Initialisez la base de données**
   Lancez un shell Python dans le répertoire du projet et exécutez les commandes suivantes :
   ```bash
   python
   ```
   Puis dans l'interpréteur Python :
   ```python
   from app import db
   db.create_all()
   exit()
   ```

4. **Démarrez le serveur**
   Lancez l'application Flask :
   ```bash
   python app.py
   ```

5. **Accédez à l'application**
   Ouvrez un navigateur et accédez à [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Utilisation

- **Inscription** : Créez un compte via la page d'inscription.
- **Connexion** : Connectez-vous avec vos identifiants.
- **Enregistrer un match** : Ajoutez un match avec les informations sur l'adversaire et les points.
- **Classement** : Consultez le classement mis à jour automatiquement après chaque match.
- **Suppression de compte** : Supprimez votre compte (attention, irréversible !).

## Structure du projet

- `app.py` : Fichier principal contenant la logique Flask.
- `templates/` : Contient les fichiers HTML des pages web.
- `static/` : Contient les fichiers CSS et autres ressources statiques.
- `db.sqlite` : Fichier de base de données SQLite généré automatiquement.

## Détails sur la formule Elo utilisée

Ce projet implémente un système de classement Elo standard pour calculer et ajuster les scores des joueurs après chaque match.

### Formule utilisée

#### Probabilité attendue pour chaque joueur :
Pour le joueur principal (Player 1) :

$$ E_1 = \frac{1}{1 + 10^{\frac{R_2 - R_1}{400}}} $$

Pour l'adversaire (Player 2) :

$$ E_2 = \frac{1}{1 + 10^{\frac{R_1 - R_2}{400}}} $$

- \(R_1\) : Score Elo actuel du joueur 1.
- \(R_2\) : Score Elo actuel du joueur 2.
- \(E_1\) et \(E_2\) : Scores attendus pour chaque joueur (entre 0 et 1).

#### Mise à jour des scores Elo :
Pour le joueur principal (Player 1) :
\[
R_1' = R_1 + K \cdot (S_1 - E_1)
\]

Pour l'adversaire (Player 2) :
\[
R_2' = R_2 + K \cdot (S_2 - E_2)
\]

- \(K\) : Constante de développement définissant l'impact maximal d'un match sur le score Elo. Dans ce projet, \(K = 32\).
- \(S_1\) et \(S_2\) : Résultats du match :
  - \(S_1 = 1\) si Player 1 gagne, \(0.5\) pour un match nul, \(0\) pour une défaite.
  - \(S_2 = 1 - S_1\).

### Implémentation

La formule est implémentée dans le fichier `app.py` comme suit :

```python
def elo_rating(player_elo, opponent_elo, result, k=32):
    expected_score_player = 1 / (1 + math.pow(10, (opponent_elo - player_elo) / 400))
    expected_score_opponent = 1 / (1 + math.pow(10, (player_elo - opponent_elo) / 400))
    new_player_elo = player_elo + k * (result - expected_score_player)
    new_opponent_elo = opponent_elo + k * (1 - result - expected_score_opponent)
    return new_player_elo, new_opponent_elo
```
### Points importants :

	1.	Constante (K = 32) : Détermine l’amplitude des variations de score après un match. Une valeur plus élevée augmente l’impact d’un match.
	2.	Basé sur les probabilités attendues : Le système pondère les gains en fonction des écarts Elo entre les joueurs. Une victoire contre un adversaire plus fort rapporte plus de points.
	3.	Modèle symétrique : Les gains d’un joueur correspondent exactement aux pertes de l’autre.

> Ce système est couramment utilisé pour évaluer les performances dans des environnements compétitifs comme les échecs, les jeux vidéo, ou ici, le babyfoot.

---