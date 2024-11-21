from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Connect to SQLite
def connect_db():
    conn = sqlite3.connect("babyfoot.db")
    return conn

# Create tables
def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        elo INTEGER DEFAULT 1200
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player1_id INTEGER,
        player2_id INTEGER,
        result TEXT,
        points INTEGER
    )""")
    conn.commit()
    conn.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, elo FROM users WHERE username = ? AND password = ?", 
                   (data["username"], data["password"]))
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({"id": user[0], "elo": user[1]})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                       (data["username"], data["password"]))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already taken"}), 400
    conn.close()
    return jsonify({"message": "User registered"})

@app.route("/update-elo", methods=["POST"])
def update_elo():
    data = request.json
    conn = connect_db()
    cursor = conn.cursor()
    # Fetch current elos
    cursor.execute("SELECT elo FROM users WHERE id = ?", (data["player1_id"],))
    p1_elo = cursor.fetchone()[0]
    cursor.execute("SELECT elo FROM users WHERE id = ?", (data["player2_id"],))
    p2_elo = cursor.fetchone()[0]

    # Update elos (simple example formula)
    k = 32
    expected1 = 1 / (1 + 10 ** ((p2_elo - p1_elo) / 400))
    expected2 = 1 / (1 + 10 ** ((p1_elo - p2_elo) / 400))

    if data["result"] == "win":
        p1_elo += k * (1 - expected1)
        p2_elo += k * (0 - expected2)
    else:
        p1_elo += k * (0 - expected1)
        p2_elo += k * (1 - expected2)

    # Save updates
    cursor.execute("UPDATE users SET elo = ? WHERE id = ?", (int(p1_elo), data["player1_id"]))
    cursor.execute("UPDATE users SET elo = ? WHERE id = ?", (int(p2_elo), data["player2_id"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Elo updated"})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
