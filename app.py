from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import math
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)

# Modèle de la base de données
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    elo = db.Column(db.Integer, default=1000)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    winner_id = db.Column(db.Integer, nullable=False)  # 1 for player1, 2 for player2
    points = db.Column(db.Integer, nullable=False)

# Fonction pour calculer le classement Elo
def elo_rating(player_elo, opponent_elo, result, point_gap, k=32, gap=20):
    """
    Calcule le nouveau score Elo d'un joueur en fonction du résultat du match et de l'écart de points.
    :param player_elo: Elo actuel du joueur.
    :param opponent_elo: Elo actuel de l'adversaire.
    :param result: Résultat du match (1 pour victoire, 0 pour défaite, 0.5 pour match nul).
    :param point_gap: Écart de score.
    :param k: Coefficient de base pour l'ajustement de l'Elo.
    :param gap: Facteur pour normaliser l'écart de score.
    :return: Nouveau score Elo du joueur.
    """
    scale_factor = min(2, 1 + (point_gap / gap))  # Pondération en fonction de l'écart de score
    adjusted_k = k * scale_factor

    expected_score = 1 / (1 + math.pow(10, (opponent_elo - player_elo) / 400))
    new_elo = player_elo + adjusted_k * (result - expected_score)
    return max(0, round(new_elo))

def calculate_team_elo(team, opponents):
    """
    Calcule le score attendu pour une équipe contre une autre.
    :param team: Liste des joueurs de l'équipe (objets User).
    :param opponents: Liste des joueurs de l'équipe adverse (objets User).
    :return: Score attendu pour l'équipe.
    """
    total_expected = 0
    for player in team:
        expected_scores = [
            1 / (1 + math.pow(10, (opponent.elo - player.elo) / 400)) for opponent in opponents
        ]
        total_expected += sum(expected_scores) / len(opponents)
    print("tot", total_expected / len(team))
    return total_expected / len(team)

# Routes de l'application
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Récupérer l'utilisateur connecté
    user = User.query.get(session['user_id'])
    
    # Récupérer tous les utilisateurs triés par Elo, du plus haut au plus bas
    leaderboard = User.query.order_by(User.elo.desc()).all()
    
    return render_template('index.html', user=user, leaderboard=leaderboard)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        return 'Nom d\'utilisateur ou mot de passe incorrect', 400
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validation des caractères dans le pseudo
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return "Nom d'utilisateur invalide. Seuls les lettres, chiffres, tirets et underscores sont autorisés.", 400
        
        # Validation des caractères dans le mot de passe
        if not re.match(r'^[a-zA-Z0-9!@#$%^&*()_+-=]+$', password):
            return "Mot de passe invalide. Les caractères spéciaux comme espaces, crochets, ou accolades ne sont pas autorisés.", 400
        
        # Vérifier si les mots de passe correspondent
        if password != confirm_password:
            return "Les mots de passe ne correspondent pas.", 400
        
        # Hachage et enregistrement
        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash)
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            return f"Erreur : {e}", 400

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Récupérer l'utilisateur connecté
    user = User.query.get(session['user_id'])
    
    # Supprimer les matchs associés à l'utilisateur
    Match.query.filter((Match.player1_id == user.id) | (Match.player2_id == user.id)).delete()

    # Supprimer l'utilisateur
    db.session.delete(user)
    db.session.commit()

    # Supprimer l'utilisateur de la session
    session.pop('user_id', None)

    return redirect(url_for('login'))

@app.route('/play_match', methods=['POST'])
def play_match():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Récupérer l'utilisateur connecté
    player1 = User.query.get(session['user_id'])
    
    # Récupération des informations depuis le formulaire
    match_type = request.form['match_type']
    points = int(request.form['points'])
    print('points:', points)
    winner = int(request.form['winner'])  # 1 pour player1 ou son équipe, 2 pour adversaire
    print('winner:', winner, '- 1 pour player1 ou son équipe, 2 pour adversaire')

    # Initialisation des équipes
    team1 = [player1]
    team2 = []

    if match_type == "1v1":
        player2_username = request.form['player2_username'].strip()
        player2 = User.query.filter_by(username=player2_username).first()
        if not player2:
            return "Adversaire introuvable.", 404
        if player2.username == player1.username:
            return "Vous ne pouvez pas jouer contre vous-même.", 400
        team2 = [player2]
        print('team1', team1)
        print('team2', team2)

    elif match_type == "1v2":
        player2_username = request.form['player2_username'].strip()
        player2_teammate_username = request.form['player2_teammate'].strip()
        player2 = User.query.filter_by(username=player2_username).first()
        player2_teammate = User.query.filter_by(username=player2_teammate_username).first()
        if not player2 or not player2_teammate:
            return "Adversaire ou coéquipier introuvable.", 404
        if player2.username == player1.username or player2_teammate.username == player1.username:
            return "Vous ne pouvez pas jouer contre vous-même.", 400
        team2 = [player2, player2_teammate]
        print('team1', team1)
        print('team2', team2)

    elif match_type == "2v1":
        teammate_username = request.form['teammate_username'].strip()
        player2_username = request.form['player2_username'].strip()
        teammate = User.query.filter_by(username=teammate_username).first()
        player2 = User.query.filter_by(username=player2_username).first()
        if not teammate or not player2:
            return "Coéquipier ou adversaire introuvable.", 404
        if teammate.username == player1.username or player2.username == player1.username:
            return "Vous ne pouvez pas jouer contre vous-même.", 400
        team1 = [player1, teammate]
        team2 = [player2]
        print('team1', team1)
        print('team2', team2)

    elif match_type == "2v2":
        teammate_username = request.form['teammate_username'].strip()
        player2_username = request.form['player2_username'].strip()
        player2_teammate_username = request.form['player2_teammate'].strip()
        teammate = User.query.filter_by(username=teammate_username).first()
        player2 = User.query.filter_by(username=player2_username).first()
        player2_teammate = User.query.filter_by(username=player2_teammate_username).first()
        if not teammate or not player2 or not player2_teammate:
            return "Joueurs introuvables.", 404
        if teammate.username == player1.username or player2.username == player1.username or player2_teammate.username == player1.username:
            return "Vous ne pouvez pas jouer contre vous-même.", 400
        team1 = [player1, teammate]
        team2 = [player2, player2_teammate]
        print('team1', team1)
        print('team2', team2)

    # Calcul des scores attendus pour les équipes
    expected_team1 = calculate_team_elo(team1, team2)
    expected_team2 = calculate_team_elo(team2, team1)

    # Application des scores aux joueurs
    for player in team1:
        result = 1 if winner == 1 else 0
        # Utilise la moyenne du Elo des adversaires
        opponent_elo = sum([opponent.elo for opponent in team2]) / len(team2)
        player.elo = elo_rating(player.elo, opponent_elo, result, points)
        print(f"Joueur {player.username} (team1) - Nouveau Elo: {player.elo}")

    for player in team2:
        result = 1 if winner == 2 else 0
        # Utilise la moyenne du Elo des adversaires
        opponent_elo = sum([opponent.elo for opponent in team1]) / len(team1)
        player.elo = elo_rating(player.elo, opponent_elo, result, points)
        print(f"Joueur {player.username} (team2) - Nouveau Elo: {player.elo}")


    # Enregistrer le match
    print(player1.id, team2[0].id if team2 else None, team1[0].id if winner == 1 else team2[0].id, points)
    match = Match(
        player1_id=player1.id,
        player2_id=team2[0].id if team2 else None,
        winner_id=team1[0].id if winner == 1 else team2[0].id,
        points=points
    )
    db.session.add(match)
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Supprimer l'utilisateur de la session
    return redirect(url_for('login'))  # Rediriger vers la page de connexion

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Créer les tables si elles n'existent pas
    app.run(debug=True)
