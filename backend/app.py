from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from sqlalchemy import text
import pymysql
import os

app = Flask(__name__)
CORS(app)

pymysql.install_as_MySQLdb()

# Configuration de la base de données
try:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.environ['MYSQL_USER']}:{os.environ['MYSQL_PASSWORD']}@{os.environ['MYSQL_HOST']}/{os.environ['MYSQL_DATABASE']}"
    print("Connexion à la base de données configurée avec succès.") # message de confirmation
except KeyError as e:
    print(f"Erreur : Variable d'environnement manquante : {e}")
    exit(1) # Arrête l'application si les variables ne sont pas définies

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Définition du modèle utilisateur
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


print("=== Configuration de la base de données ===")
print(f"MYSQL_HOST: {os.environ['MYSQL_HOST']}")
print(f"MYSQL_USER: {os.environ['MYSQL_USER']}")
print(f"MYSQL_DATABASE: {os.environ['MYSQL_DATABASE']}")

# Création des tables (à exécuter une seule fois)
with app.app_context():
    db.create_all()

@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'message': 'No JSON data provided'}), 400

            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            if not username or not email or not password:
                return jsonify({'message': 'Username, email and password are required'}), 400

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return jsonify({'message': 'Username already exists'}), 409

            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                return jsonify({'message': 'Email already exists'}), 409

            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            return jsonify({'message': 'User added successfully'}), 201

        except Exception as e:
            db.session.rollback()  # Très important en cas d'erreur avec la base de données
            print(f"Erreur lors de l'ajout de l'utilisateur : {str(e)}")
            return jsonify({'message': f'Error: {str(e)}'}), 500
    else:
        return jsonify({'message': 'Method not allowed'}), 405

@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()  # Récupère tous les utilisateurs de la base de données
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
        return jsonify(user_list), 200  # Retourne la liste des utilisateurs au format JSON
    except Exception as e:
        print(f"Erreur lors de la récupération des utilisateurs : {e}")
        return jsonify({'message': f'Erreur : {str(e)}'}), 500

def test_db_connection():
    try:
        with app.app_context():
            with db.engine.connect() as connection:
                print("Connexion à la base de données réussie!")
                return True
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return False

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user_route(user_id):
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except ValueError:
        return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    

test_db_connection()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)