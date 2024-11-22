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

---