from datetime import datetime
from app import db


class Supplier(db.Model):
    """Modelo que representa a un proveedor del negocio."""

    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    contacto = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    telefono = db.Column(db.String(30), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)
    saldo_pendiente = db.Column(db.Float, default=0.0, nullable=False)
    estado = db.Column(db.String(20), default='Activo', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'contacto': self.contacto,
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'saldo_pendiente': self.saldo_pendiente,
            'estado': self.estado,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Supplier {self.nombre}>'
