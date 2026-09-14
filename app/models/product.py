from datetime import datetime
from app import db


class Product(db.Model):
    """Modelo que representa un producto del catálogo."""

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)  
    descripcion = db.Column(db.String(300), nullable=True)
    precio = db.Column(db.Float, default=0.0, nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    categoria = db.Column(db.String(80), nullable=True)
    estado = db.Column(db.String(20), default='Activo', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convierte el producto a diccionario para JSON."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'sku': self.sku,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'stock': self.stock,
            'categoria': self.categoria,
            'estado': self.estado,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Product {self.nombre}>'