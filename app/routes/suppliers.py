from flask import Blueprint, request, jsonify
from flask_login import login_required
from app import db
from app.models.supplier import Supplier

bp = Blueprint('suppliers', __name__, url_prefix='/api/suppliers')


# LISTAR: GET /api/suppliers
@bp.route('/', methods=['GET'])
@login_required
def list_suppliers():
    """Devuelve la lista de todos los proveedores."""
    proveedores = Supplier.query.order_by(Supplier.nombre).all()
    return jsonify({
        'success': True,
        'total': len(proveedores),
        'proveedores': [p.to_dict() for p in proveedores]
    })


# VER UNO: GET /api/suppliers/<id>
@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_supplier(id):
    """Devuelve un proveedor específico."""
    proveedor = Supplier.query.get(id)
    if not proveedor:
        return jsonify({'success': False, 'error': 'Proveedor no encontrado'}), 404
    return jsonify({'success': True, 'proveedor': proveedor.to_dict()})


# CREAR: POST /api/suppliers
@bp.route('/', methods=['POST'])
@login_required
def create_supplier():
    """Crea un nuevo proveedor."""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400

    nombre = (data.get('nombre') or '').strip()
    contacto = (data.get('contacto') or '').strip()
    email = (data.get('email') or '').strip().lower()
    telefono = (data.get('telefono') or '').strip()
    direccion = (data.get('direccion') or '').strip()
    saldo_pendiente = data.get('saldo_pendiente', 0.0)

    if not nombre or not email:
        return jsonify({'success': False, 'error': 'Nombre y email son obligatorios'}), 400

    if Supplier.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'Ese email ya está registrado'}), 409

    proveedor = Supplier(
        nombre=nombre,
        contacto=contacto,
        email=email,
        telefono=telefono,
        direccion=direccion,
        saldo_pendiente=float(saldo_pendiente),
        estado='Activo'
    )
    db.session.add(proveedor)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Proveedor "{nombre}" creado exitosamente',
        'proveedor': proveedor.to_dict()
    }), 201



# EDITAR: PUT /api/suppliers/<id>
@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_supplier(id):
    """Actualiza un proveedor existente."""
    proveedor = Supplier.query.get(id)
    if not proveedor:
        return jsonify({'success': False, 'error': 'Proveedor no encontrado'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400

    nombre = (data.get('nombre') or proveedor.nombre).strip()
    contacto = (data.get('contacto') or '').strip()
    email = (data.get('email') or proveedor.email).strip().lower()
    telefono = (data.get('telefono') or '').strip()
    direccion = (data.get('direccion') or '').strip()
    saldo_pendiente = data.get('saldo_pendiente', proveedor.saldo_pendiente)
    estado = data.get('estado', proveedor.estado)

    if not nombre or not email:
        return jsonify({'success': False, 'error': 'Nombre y email son obligatorios'}), 400

    existente = Supplier.query.filter_by(email=email).first()
    if existente and existente.id != id:
        return jsonify({'success': False, 'error': 'Ese email ya está en uso'}), 409

    proveedor.nombre = nombre
    proveedor.contacto = contacto
    proveedor.email = email
    proveedor.telefono = telefono
    proveedor.direccion = direccion
    proveedor.saldo_pendiente = float(saldo_pendiente)
    proveedor.estado = estado
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Proveedor actualizado exitosamente',
        'proveedor': proveedor.to_dict()
    })


# ELIMINAR: DELETE /api/suppliers/<id>
@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_supplier(id):
    """Elimina un proveedor."""
    proveedor = Supplier.query.get(id)
    if not proveedor:
        return jsonify({'success': False, 'error': 'Proveedor no encontrado'}), 404

    nombre = proveedor.nombre
    db.session.delete(proveedor)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Proveedor "{nombre}" eliminado correctamente'
    })

        