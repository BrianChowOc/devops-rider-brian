import mysql.connector
import os
import click
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST") or "localhost",
            user=os.environ.get("MYSQL_USER") or "root",
            password=os.environ.get("MYSQL_ROOT_PASSWORD") or "root",
            database=os.environ.get("MYSQL_DATABASE") or "yourdatabase"
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cursor = db.cursor()
    with current_app.open_resource('schema.sql') as f:
        sql_script = f.read().decode('utf8')
        cursor.execute(sql_script, multi=True)
    db.commit()

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.cli.add_command(init_db_command)