import sqlite3

DB_PATH = './database/database.db'

def create_connection():
    """Créer une connexion à la base de données SQLite"""
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_table():
    """Créer une table 'users' si elle n'existe pas déjà"""
    conn = create_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.close()

def insert_user(username, email, password):
    """Insérer un utilisateur dans la base de données"""
    conn = create_connection()
    conn.execute('''
        INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)
    ''', (username, email, password))
    conn.commit()
    conn.close()

def get_users():
    """Récupérer tous les utilisateurs"""
    conn = create_connection()
    cursor = conn.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users
