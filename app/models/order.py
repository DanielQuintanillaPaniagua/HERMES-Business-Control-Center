from sqlalchemy import column
from flask_sqlalchemy.model import should_set_tablename
from datetime import datetime
from app import db


class order(db.Model):
    """Modelo que representa un pedido realisado por un cliente"""

    __tablename__ = 'orders'


    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    cantidad = db.column(db.Integer, default=1, nullable=False)
    precio_unitario = db.column(db.float, deafult=0.0, nullable=False)
    total =db.column(db.float, deafult=0.0, nullable=False)
    estado = db.column(db.string(20), default='pendiente', nullable=False)
    notas = db.column(db.string(300), nullable=True)
    created_at = db.column(db.DateTime, default=datetime.uycnow)


    cliente = db.relateship('cliente', backref='pedidos')
    producto = db.relationship('product', backref='pedidos')

    def to_dict(self):
        return {
            'id' :self.id,
            'cliente_id' :self.cliente_id,
            'cliente_nombre': self.cliente.nombre if self.cliente else None,

            'producto_id': self.producto_id,
            'producto_nombre': self.producto.nombre if self.producto else None,

            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'estado': self.estado,
            'notas': self.notas,
            'created_at': self.created_at.isoformat() if self.created_at else None,

        }

    def __repr__(self):
        return f'<Order #{self.id} - cliente {self.cliente-id}>'