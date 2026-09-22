# app/models/invoice.py
# Modelo de Factura para HERMES

from datetime import datetime, date
from app import db


class Invoice(db.Model):
    """Modelo que representa una factura del negocio."""

    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    fecha_emision = db.Column(db.Date, default=date.today, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    concepto = db.Column(db.String(200), nullable=False)
    total = db.Column(db.Float, default=0.0, nullable=False)
    estado = db.Column(db.String(20), default='Pendiente', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacion con Cliente
    cliente = db.relationship('Client', backref='facturas')

    def to_dict(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'client_id': self.client_id,
            'cliente_nombre': self.cliente.nombre if self.cliente else None,
            'fecha_emision': self.fecha_emision.isoformat() if self.fecha_emision else None,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'concepto': self.concepto,
            'total': self.total,
            'estado': self.estado,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Invoice {self.numero}>'
