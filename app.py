from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
from database import get_db, close_db, init_db
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/images'
app.teardown_appcontext(close_db)

# Inicializar base de datos
with app.app_context():
    init_db()

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelo de usuario para Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    if user:
        return User(user['id'], user['username'])
    return None

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM proyectos LIMIT 3')  # Mostrar solo 3 proyectos en la página principal
    proyectos = cursor.fetchall()
    return render_template('index.html', proyectos=proyectos)

@app.route('/galeria')
def galeria():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM proyectos')
    proyectos = cursor.fetchall()
    return render_template('galeria.html', proyectos=proyectos)

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        mensaje = request.form['mensaje']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO mensajes (nombre, email, mensaje) VALUES (?, ?, ?)',
                       (nombre, email, mensaje))
        db.commit()
        flash('¡Gracias por tu mensaje! Nos pondremos en contacto pronto.', 'success')
        return redirect(url_for('contacto'))
    return render_template('contacto.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        if user:
            user_obj = User(user['id'], user['username'])
            login_user(user_obj)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        imagen = request.files['imagen']
        if imagen:
            imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen.filename)
            imagen.save(imagen_path)
            db = get_db()
            cursor = db.cursor()
            cursor.execute('INSERT INTO proyectos (titulo, descripcion, imagen) VALUES (?, ?, ?)',
                           (titulo, descripcion, imagen.filename))
            db.commit()
            flash('Proyecto agregado exitosamente.', 'success')
            return redirect(url_for('dashboard'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM proyectos')
    proyectos = cursor.fetchall()
    cursor.execute('SELECT * FROM mensajes')
    mensajes = cursor.fetchall()
    return render_template('dashboard.html', proyectos=proyectos, mensajes=mensajes)

@app.route('/eliminar_proyecto/<int:id>')
@login_required
def eliminar_proyecto(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT imagen FROM proyectos WHERE id = ?', (id,))
    proyecto = cursor.fetchone()
    if proyecto:
        imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], proyecto['imagen'])
        if os.path.exists(imagen_path):
            os.remove(imagen_path)
        cursor.execute('DELETE FROM proyectos WHERE id = ?', (id,))
        db.commit()
        flash('Proyecto eliminado exitosamente.', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)