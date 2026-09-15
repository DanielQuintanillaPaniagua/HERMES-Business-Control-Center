from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required
from app import db
from app.models.shipment import Shipment
from app.models.order import Order

bp = Blueprint('shipments', __name__, url_prefix='/api/shipments')



@bp.route('/', methods=['GET'])
@login_required
def list_shipments():
    """Devuelve la lista de todos los envíos."""
    envios = Shipment.query.order_by(Shipment.created_at.desc()).all()
    return jsonify({
        'success': True,
        'total': len(envios),
        'envios': [e.to_dict() for e in envios]
    })



@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_shipment(id):
    """Devuelve un envío específico."""
    envio = Shipment.query.get(id)
    if not envio:
        return jsonify({'success': False, 'error': 'Envío no encontrado'}), 404
    return jsonify({'success': True, 'envio': envio.to_dict()})



@bp.route('/', methods=['POST'])
@login_required
def create_shipment():
    """Crea un nuevo envío para un pedido."""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400

    pedido_id = data.get('pedido_id')
    direccion_envio = (data.get('direccion_envio') or '').strip()
    ciudad = (data.get('ciudad') or '').strip()
    transportista = (data.get('transportista') or '').strip()
    numero_guia = (data.get('numero_guia') or '').strip().upper()

    if not pedido_id or not direccion_envio:
        return jsonify({'success': False, 'error': 'Pedido y dirección de envío son obligatorios'}), 400

    pedido = Order.query.get(pedido_id)
    if not pedido:
        return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404

    if numero_guia and Shipment.query.filter_by(numero_guia=numero_guia).first():
        return jsonify({'success': False, 'error': 'Ese número de guía ya está registrado'}), 409

    fecha_entrega_estimada = None
    if data.get('fecha_entrega_estimada'):
        try:
            fecha_entrega_estimada = datetime.fromisoformat(data['fecha_entrega_estimada'])
        except ValueError:
            return jsonify({'success': False, 'error': 'Formato de fecha inválido'}), 400

    envio = Shipment(
        pedido_id=pedido.id,
        direccion_envio=direccion_envio,
        ciudad=ciudad,
        transportista=transportista,
        numero_guia=numero_guia or None,
        fecha_entrega_estimada=fecha_entrega_estimada,
        estado='Preparando'
    )
    db.session.add(envio)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Envío #{envio.id} creado exitosamente',
        'envio': envio.to_dict()
    }), 201



@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_shipment(id):
    """Actualiza un envío existente."""
    envio = Shipment.query.get(id)
    if not envio:
        return jsonify({'success': False, 'error': 'Envío no encontrado'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400

    direccion_envio = (data.get('direccion_envio') or envio.direccion_envio).strip()
    ciudad = (data.get('ciudad') or envio.ciudad or '').strip()
    transportista = (data.get('transportista') or envio.transportista or '').strip()
    numero_guia = (data.get('numero_guia') or envio.numero_guia or '').strip().upper()
    estado = data.get('estado', envio.estado)

    if not direccion_envio:
        return jsonify({'success': False, 'error': 'La dirección de envío es obligatoria'}), 400

    existente = Shipment.query.filter_by(numero_guia=numero_guia).first() if numero_guia else None
    if existente and existente.id != id:
        return jsonify({'success': False, 'error': 'Ese número de guía ya está en uso'}), 409

    fecha_envio = envio.fecha_envio
    if data.get('fecha_envio'):
        try:
            fecha_envio = datetime.fromisoformat(data['fecha_envio'])
        except ValueError:
            return jsonify({'success': False, 'error': 'Formato de fecha de envío inválido'}), 400

    fecha_entrega_estimada = envio.fecha_entrega_estimada
    if data.get('fecha_entrega_estimada'):
        try:
            fecha_entrega_estimada = datetime.fromisoformat(data['fecha_entrega_estimada'])
        except ValueError:
            return jsonify({'success': False, 'error': 'Formato de fecha estimada inválido'}), 400

    envio.direccion_envio = direccion_envio
    envio.ciudad = ciudad
    envio.transportista = transportista
    envio.numero_guia = numero_guia or None
    envio.estado = estado
    envio.fecha_envio = fecha_envio
    envio.fecha_entrega_estimada = fecha_entrega_estimada
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Envío actualizado exitosamente',
        'envio': envio.to_dict()
    })



@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_shipment(id):
    """Elimina un envío."""
    envio = Shipment.query.get(id)
    if not envio:
        return jsonify({'success': False, 'error': 'Envío no encontrado'}), 404

    db.session.delete(envio)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Envío #{id} eliminado correctamente'
    })