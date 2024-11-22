from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import math

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
def elo_rating(player_elo, opponent_elo, result, k=32):
    expected_score_player = 1 / (1 + math.pow(10, (opponent_elo - player_elo) / 400))
    expected_score_opponent = 1 / (1 + math.pow(10, (player_elo - opponent_elo) / 400))
    new_player_elo = player_elo + k * (result - expected_score_player)
    new_opponent_elo = opponent_elo + k * (1 - result - expected_score_opponent)
    return new_player_elo, new_opponent_elo

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
        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
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
    
    # Récupérer le pseudo de l'adversaire
    player2_username = request.form['player2_username']
    points = int(request.form['points'])

    # Chercher l'adversaire par son pseudo
    player2 = User.query.filter_by(username=player2_username).first()

    # Vérifier que l'adversaire existe
    if not player2:
        return "L'adversaire n'a pas été trouvé", 404

    # Déterminer qui a gagné
    winner = request.form['winner']
    
    if winner == '1':
        winner_id = player1.id
        result = 1  # Player 1 wins
    else:
        winner_id = player2.id
        result = 0  # Player 2 wins

    # Calcul Elo
    new_player1_elo, new_player2_elo = elo_rating(player1.elo, player2.elo, result)

    # Mise à jour des Elo dans la base de données
    player1.elo = round(new_player1_elo)
    player2.elo = round(new_player2_elo)

    # Enregistrer le match
    match = Match(player1_id=player1.id, player2_id=player2.id, winner_id=winner_id, points=points)
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
