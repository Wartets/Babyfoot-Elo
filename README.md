# Babyfoot Elo - Système de Classement ELO

Ce projet est une application web pour gérer les classements ELO des joueurs de babyfoot. Voici comment l'utiliser en local.

## Prérequis

- Python 3.x minimun installé
- SQLite (inclus avec Python)
- Navigateur web

## Installation et configuration

1. **Clonez ce dépôt** (ou télechargez la dernière release)
   ```bash
   git clone https://github.com/wartets/babyfoot-elo.git
   cd babyfoot-elo
   ```

2. **Installez les dépendances nécessaires**
   Installez Flask et les autres dépendances nécessaires à l'application en utilisant la commande suivante :
   ```bash
   pip install flask flask-sqlalchemy werkzeug
   ```

3. **Initialisez la base de données** (si elle n'existe déjà pas)
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
   Lancez l'application Flask dans le répoertoire du projet :
   ```bash
   cd {répertoire du projet}
   python app.py
   ```

5. **Accédez à l'application**
   Ouvrez un navigateur et accédez à l'adresse locale : [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Utilisation

- **Inscription** : Créez un compte via la page d'inscription.
- **Connexion** : Connectez-vous avec vos identifiants.
- **Enregistrer un match** : Ajoutez un match en renseignant les participants, le type de partie (1v1, 1v2, 2v1, ou 2v2) et l'écart de points final.
- **Classement** : Consultez le classement mis à jour automatiquement après chaque match.
- **Suppression de compte** : Supprimez votre compte (attention, cette action est irréversible !).

## Structure du projet

- `app.py` : Fichier principal contenant la logique Flask.
- `templates/` : Contient les fichiers HTML des pages web.
- `static/` : Contient les fichiers CSS et autres ressources statiques.
- `db.sqlite` : Fichier de base de données SQLite généré automatiquement.

## Détails sur le système Elo

Ce projet implémente un système de classement Elo ajusté pour le babyfoot, prenant en charge différents formats de parties (1v1, 1v2, 2v1, 2v2). Les scores des joueurs sont mis à jour après chaque match en fonction des résultats et des performances attendues.

### Calcul des probabilités attendues

Pour chaque joueur, la probabilité de victoire est calculée comme suit :

Pour un joueur ou une équipe A contre un joueur ou une équipe B :
```
E_A = 1 / (1 + 10^((R_B - R_A) / 400))
```
- **R_A** : Score Elo actuel de l'équipe/joueur A.
- **R_B** : Score Elo actuel de l'équipe/joueur B.
- **E_A** : Probabilité attendue pour l'équipe/joueur A (valeur entre 0 et 1).

### Mise à jour des scores Elo

Après le match, les scores Elo sont mis à jour en fonction de l'écart de points final et du résultat :
```
R_A' = R_A + K * (S_A - E_A) * scale_factor
```
- **S_A** : Résultat du match pour l'équipe/joueur A (1 pour victoire, 0.5 pour égalité, 0 pour défaite).
- **scale_factor** : Facteur de pondération basé sur l'écart de points final.
- **K** : Constante d'ajustement (par défaut, K = 32).
- **R_A'** : Nouveau score Elo de l'équipe/joueur A.

Le `scale_factor` est calculé en fonction de l'écart de score :
```
scale_factor = min(2, 1 + (point_gap / gap))
```
où **point_gap** est l'écart de score final et **gap** est une constante définissant la sensibilité à cet écart.

### Gestion des parties en équipe

Pour les parties 1v2 ou 2v2, les probabilités attendues et les mises à jour de scores sont calculées pour chaque joueur individuellement en tenant compte de l'Elo moyen des adversaires.

### Points importants :

1.	Constante (K = 32) : Détermine l’amplitude des variations de score après un match. Une valeur plus élevée augmente l’impact d’un match.
2. **Flexibilité des formats** : Les formules s'appliquent aux parties en 1v1, 1v2, 2v1 et 2v2.
3. **Impact de l'écart de score** : Les gains/pertes de points sont amplifiés pour les victoires écrasantes.
4.	Basé sur les probabilités attendues : Le système pondère les gains en fonction des écarts Elo entre les joueurs. Une victoire contre un adversaire plus fort rapporte plus de points.
5. **Modèle symétrique** : Les gains d'une équipe ou d'un joueur correspondent exactement aux pertes de l'autre.

---