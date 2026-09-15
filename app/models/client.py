# app/models/client.py
from datetime import datetime
from app import db


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    telefono = db.Column(db.String(30), nullable=True)
    ciudad = db.Column(db.String(80), nullable=True)
    estado = db.Column(db.String(20), default="Activo", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Client {self.nombre}>"


