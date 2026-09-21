from flask import Blueprint, jsonify
from flask_login import login_required
from datetime import datetime
from app import db
from app.models.order import Order
from app.models.shipment import Shipment

bp = Blueprint('dashboard_activities', __name__, url_prefix='/api/dashboard')


def _hace_cuanto(fecha):
    """Convierte una fecha en 'Hace X min/horas/días'."""
    if not fecha:
        return 'Desconocido'
    diff = datetime.utcnow() - fecha
    segundos = diff.total_seconds()
    if segundos < 60:
        return 'Hace un momento'
    if segundos < 3600:
        return f"Hace {int(segundos // 60)} min"
    if segundos < 86400:
        return f"Hace {int(segundos // 3600)} horas"
    return f"Hace {int(segundos // 86400)} días"


@bp.route('/activities', methods=['GET'])
@login_required
def activities():
    """Devuelve las actividades recientes (pedidos y envíos)."""
    actividades = []

    # Últimos 3 pedidos
    ultimos_pedidos = Order.query.order_by(Order.created_at.desc()).limit(3).all()
    for p in ultimos_pedidos:
        actividades.append({
            'tipo': 'pedido',
            'texto': f'Pedido #{p.id} realizado',
            'tiempo': _hace_cuanto(p.created_at),
            'fecha': p.created_at.isoformat() if p.created_at else None
        })

    # Últimos 3 envíos
    ultimos_envios = Shipment.query.order_by(Shipment.created_at.desc()).limit(3).all()
    for e in ultimos_envios:
        actividades.append({
            'tipo': 'envio',
            'texto': f'Envío #{e.numero_guia or e.id} ({e.estado})',
            'tiempo': _hace_cuanto(e.created_at),
            'fecha': e.created_at.isoformat() if e.created_at else None
        })

    # Ordenar por fecha descendente
    actividades.sort(key=lambda x: x['fecha'] or '', reverse=True)

    return jsonify({
        'success': True,
        'activities': actividades[:6]
    })
