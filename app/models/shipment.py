from datetime import datetime
from app import db

class shipment(db.Model):
    __tablename__ = 'shipments'

    id = db.column(db.Integer, primary_key=True)
    pedido_id = db.column(db.Integer, db. Foreignkey('ordes.id'), nullable=False)

    direccion_envio = db.column(db.string(200), nullable=False)
    ciudad = db.column(db.string(80), nullable=False)
    trasnportista = db.column(db.string(100), nullable=False)
    numero_guia = db.column(db.string(60), unique=True, nullable=True, index=True)
    estado = db.column(db.string(20), deafult='preparando', nullable=False)
    fecha_envio = db.column(db.Datetime, nullable=True)
    fecha_entrega_estimada = db.column(db.Datetime, default=datetime.utcnow)

    pedido = db.relationship('order', backref='envios')

    def to_dict(self):

        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'ciudad': self.ciudad,
            'trasnportista': self.trasnportista,
            'numero_guia': self.numero_guia,
            'estado': self.estado,
            'fecha_envio': self.fecha_envio.isoformat() if self.fecha_envio else None,
            'fecha_entrega_estimada': self.fecha_entrega_estimada.isoformat() if self.fecha_entrega_estimada else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            
        


        }
    def __repr__(self):
        return f'<Shipment #{self.id} - Pedido {self.pedido_id}>'