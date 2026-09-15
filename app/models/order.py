from datetime import datetime
from app import db


class Order(db.Model):
    """Modelo que representa un pedido realizado por un cliente."""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    cantidad = db.Column(db.Integer, default=1, nullable=False)
    precio_unitario = db.Column(db.Float, default=0.0, nullable=False)
    total = db.Column(db.Float, default=0.0, nullable=False)
    estado = db.Column(db.String(20), default="pendiente", nullable=False)
    notas = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cliente = db.relationship("Client", backref="pedidos")
    producto = db.relationship("Product", backref="pedidos")

    def to_dict(self):
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "cliente_nombre": self.cliente.nombre if self.cliente else None,
            "producto_id": self.producto_id,
            "producto_nombre": self.producto.nombre if self.producto else None,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "total": self.total,
            "estado": self.estado,
            "notas": self.notas,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Order #{self.id} - Cliente {self.cliente_id}>"
