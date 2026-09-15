from datetime import datetime
from app import db


class Shipment(db.Model):
    """Modelo que representa un envío asociado a un pedido."""

    __tablename__ = "shipments"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)

    direccion_envio = db.Column(db.String(200), nullable=False)
    ciudad = db.Column(db.String(80), nullable=False)
    transportista = db.Column(db.String(100), nullable=False)
    numero_guia = db.Column(db.String(60), unique=True, nullable=True, index=True)
    estado = db.Column(db.String(20), default="preparando", nullable=False)
    fecha_envio = db.Column(db.DateTime, nullable=True)
    fecha_entrega_estimada = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pedido = db.relationship("Order", backref="envios")

    def to_dict(self):
        return {
            "id": self.id,
            "pedido_id": self.pedido_id,
            "direccion_envio": self.direccion_envio,
            "ciudad": self.ciudad,
            "transportista": self.transportista,
            "numero_guia": self.numero_guia,
            "estado": self.estado,
            "fecha_envio": self.fecha_envio.isoformat() if self.fecha_envio else None,
            "fecha_entrega_estimada": self.fecha_entrega_estimada.isoformat() if self.fecha_entrega_estimada else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Shipment #{self.id} - Pedido {self.pedido_id}>"
