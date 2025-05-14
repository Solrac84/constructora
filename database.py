import sqlite3
from flask import g

DATABASE = 'instance/constructora.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Tabla para proyectos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proyectos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                imagen TEXT NOT NULL
            )
        ''')
        # Tabla para mensajes de contacto
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email TEXT NOT NULL,
                mensaje TEXT NOT NULL
            )
        ''')
        # Tabla para usuarios (para autenticación)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        # Insertar un usuario administrador por defecto (username: admin, password: admin123)
        cursor.execute('''
            INSERT OR IGNORE INTO usuarios (username, password) VALUES (?, ?)
        ''', ('admin', 'admin123'))  # En producción, usa hash para contraseñas
        conn.commit()

def close_db(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()