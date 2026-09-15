from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User

# Creamos el Blueprint 'auth'
bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de nuevos usuarios."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not username or not email or not password:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('La contraseÃ±a debe tener al menos 6 caracteres', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Ese email ya estÃ¡ registrado', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=username).first():
            flash('Ese nombre de usuario ya estÃ¡ en uso', 'danger')
            return redirect(url_for('auth.register'))
        
        nuevo_usuario = User(username=username, email=email)
        nuevo_usuario.set_password(password)
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        login_user(nuevo_usuario)
        flash(f'Â¡Cuenta creada exitosamente! Bienvenido, {username}', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Inicio de sesiÃ³n."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        usuario = User.query.filter_by(email=email).first()
        
        if usuario is None or not usuario.check_password(password):
            flash('Email o contraseÃ±a incorrectos', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(usuario)
        flash(f'Â¡Bienvenido de nuevo, {usuario.username}!', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    """Cierre de sesiÃ³n."""
    logout_user()
    flash('Has cerrado sesiÃ³n correctamente', 'info')
    return redirect(url_for('auth.login'))
