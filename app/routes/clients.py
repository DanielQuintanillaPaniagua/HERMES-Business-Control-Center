from flask import Blueprint, request, jsonify
from flask_login import login_required
from app import db
from app.models.client import Client

bp = Blueprint('clients', __name__, url_prefix='/api/clients')


# LISTAR: GET /api/clients
@bp.route('/', methods=['GET'])
@login_required
def list_clients():
    """Devuelve la lista de todos los clientes en JSON."""
    clientes = Client.query.order_by(Client.nombre).all()
    return jsonify({
        'success': True,
        'total': len(clientes),
        'clientes': [c.to_dict() for c in clientes]
    })


# VER UNO: GET /api/clients/<id>
@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_client(id):
    """Devuelve un cliente específico."""
    cliente = Client.query.get(id)
    if not cliente:
        return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
    return jsonify({'success': True, 'cliente': cliente.to_dict()})


# CREAR: POST /api/clients
@bp.route('/', methods=['POST'])
@login_required
def create_client():
    """Crea un nuevo cliente desde JSON."""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400

    nombre = (data.get('nombre') or '').strip()
    email = (data.get('email') or '').strip().lower()
    telefono = (data.get('telefono') or '').strip()
    ciudad = (data.get('ciudad') or '').strip()

    if not nombre or not email:
        return jsonify({'success': False, 'error': 'Nombre y email son obligatorios'}), 400

    if Client.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'Ese email ya está registrado'}), 409

    cliente = Client(
        nombre=nombre,
        email=email,
        telefono=telefono,
        ciudad=ciudad,
        estado='Activo'
    )
    db.session.add(cliente)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Cliente "{nombre}" creado exitosamente',
        'cliente': cliente.to_dict()
    }), 201


# EDITAR: PUT /api/clients/<id>
@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_client(id):
    """Actualiza un cliente existente."""
    cliente = Client.query.get(id)
    if not cliente:
        return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400

    nombre = (data.get('nombre') or cliente.nombre).strip()
    email = (data.get('email') or cliente.email).strip().lower()
    telefono = (data.get('telefono') or '').strip()
    ciudad = (data.get('ciudad') or '').strip()
    estado = data.get('estado', cliente.estado)

    if not nombre or not email:
        return jsonify({'success': False, 'error': 'Nombre y email son obligatorios'}), 400

    existente = Client.query.filter_by(email=email).first()
    if existente and existente.id != id:
        return jsonify({'success': False, 'error': 'Ese email ya está en uso'}), 409

    cliente.nombre = nombre
    cliente.email = email
    cliente.telefono = telefono
    cliente.ciudad = ciudad
    cliente.estado = estado
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Cliente actualizado exitosamente',
        'cliente': cliente.to_dict()
    })


# ELIMINAR: DELETE /api/clients/<id>
@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_client(id):
    """Elimina un cliente."""
    cliente = Client.query.get(id)
    if not cliente:
        return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404

    nombre = cliente.nombre
    db.session.delete(cliente)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Cliente "{nombre}" eliminado correctamente'
    })