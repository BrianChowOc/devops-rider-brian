from flask import Flask, request, jsonify, render_template
from database import get_db, close_db
import bcrypt
import os

app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config['SECRET_KEY'] = os.urandom(24)  # Clé secrète (important pour la sécurité)

def hash_password(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode('utf-8')

def check_password(password, hashed_password):
    password_bytes = password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)

@app.route('/register', methods=['POST'])
def register():
    db = get_db()
    cursor = db.cursor()
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Pas de données JSON fournies'}), 400
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({'error': 'Veuillez fournir un nom d\'utilisateur, un email et un mot de passe'}), 400

        hashed_password = hash_password(password)

        sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        val = (username, email, hashed_password)
        cursor.execute(sql, val)
        db.commit()

        return jsonify({'message': 'Utilisateur enregistré avec succès'}), 201
    except mysql.connector.errors.IntegrityError as e:
        if "Duplicate entry" in str(e):
            if "username" in str(e):
                return jsonify({'error': 'Nom d\'utilisateur déjà utilisé'}), 400
            elif "email" in str(e):
                return jsonify({'error': 'Email déjà utilisé'}), 400
        return jsonify({'error': f'Erreur lors de l\'enregistrement : {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'enregistrement : {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    db = get_db()
    cursor = db.cursor()
    try:
        data = request.get_json()
        if not data:
             return jsonify({'error': 'Pas de données JSON fournies'}), 400
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Veuillez fournir un nom d\'utilisateur et un mot de passe'}), 400

        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result :
            hashed_password = result[0]
            if check_password(password, hashed_password) :
                return jsonify({'message': 'Connexion réussie'}), 200
            else :
                return jsonify({'error': 'Mot de passe incorrect'}), 401
        else :
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

    except Exception as e:
        return jsonify({'error': f'Erreur lors de la connexion : {str(e)}'}), 500

@app.errorhandler(400)
def bad_request(error):
    return render_template('base.html', error=error.description), 400

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('base.html', error="Erreur interne du serveur"), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')