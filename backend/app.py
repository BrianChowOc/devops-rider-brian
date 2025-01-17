from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app) 

DATABASE = './database/database.db'

# Fonction pour se connecter à la base de données
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par leur nom
    return conn

# Endpoint pour initialiser la base de données
@app.route('/init_db', methods=['GET'])
def init_db():
    try:
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        return jsonify({'message': 'Base de données initialisée avec succès.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint pour ajouter un utilisateur
@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Tous les champs sont obligatoires.'}), 400

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
        (username, email, password)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Utilisateur ajouté avec succès.'}), 201

# Endpoint pour récupérer tous les utilisateurs
@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()

    user_list = [dict(user) for user in users]
    return jsonify(user_list), 200

# Endpoint pour récupérer un utilisateur par ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if user is None:
        return jsonify({'error': 'Utilisateur introuvable.'}), 404

    return jsonify(dict(user)), 200

if __name__ == '__main__':
    app.run(debug=True)
