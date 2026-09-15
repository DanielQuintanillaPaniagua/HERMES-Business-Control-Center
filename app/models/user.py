# app/models/user.py
# Modelo de Usuario para autenticaciÃ³n

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    """Modelo que representa a un usuario del sistema HERMES."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hashea y guarda la contraseÃ±a."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica si una contraseÃ±a coincide con el hash guardado."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
