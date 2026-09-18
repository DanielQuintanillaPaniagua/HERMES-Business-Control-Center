from logging import error
from sqlalchemy import except_
from sqlalchemy.sql.coercions import expect
from flask import Blueprint
from flask import Blueprint, request, jsonify
from flask_login import login_required
from app import db
from app.models.order import Order
from app.models.client import Client
from app.models.product import Product 

bp = Blueprint('orders', __name__, url_prefix='/api/orders')
 
 

@bp.route('/', methods=['GET'])
@login_required
def list_orders():
    """Devuelve la lista de todos los pedidos."""
    pedidos = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify({
        'success': True,
        'total': len(pedidos),
        'pedidos': [p.to_dict() for p in pedidos]
    })
 
 

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_order(id):
    """Devuelve un pedido especÃ­fico."""
    pedido = Order.query.get(id)
    if not pedido:
        return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
    return jsonify({'success': True, 'pedido': pedido.to_dict()})
 
 

@bp.route('/', methods=['POST'])
@login_required
def create_order():
    """Crea un nuevo pedido."""
    data = request.get_json()
 
    if not data:
        return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400
 
    cliente_id = data.get('cliente_id')
    producto_id = data.get('producto_id')
    cantidad = data.get('cantidad', 1)
    notas = (data.get('notas') or '').strip()
 
    if not cliente_id or not producto_id:
        return jsonify({'success': False, 'error': 'Cliente y producto son obligatorios'}), 400
 
    cliente = Client.query.get(cliente_id)
    if not cliente:
        return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
 
    producto = Product.query.get(producto_id)
    if not producto:
        return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
 
    try:
        cantidad = int(cantidad)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Cantidad invÃ¡lida'}), 400
 
    if cantidad <= 0:
        return jsonify({'success': False, 'error': 'La cantidad debe ser mayor a 0'}), 400
 
    if producto.stock < cantidad:
        return jsonify({'success': False, 'error': 'Stock insuficiente para este producto'}), 409
 
    precio_unitario = producto.precio
    total = round(precio_unitario * cantidad, 2)
 
    pedido = Order(
        cliente_id=cliente.id,
        producto_id=producto.id,
        cantidad=cantidad,
        precio_unitario=precio_unitario,
        total=total,
        notas=notas,
        estado='Pendiente'
    )
 
    producto.stock -= cantidad
 
    db.session.add(pedido)
    db.session.commit()
 
    return jsonify({
        'success': True,
        'message': f'Pedido #{pedido.id} creado exitosamente',
        'pedido': pedido.to_dict()
    }), 201
 
 
@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_order(id):
    """Actualiza un pedido existente."""
    pedido = Order.query.get(id)
    if not pedido:
        return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
 
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400
 
    cantidad = data.get('cantidad', pedido.cantidad)
    estado = data.get('estado', pedido.estado)
    notas = (data.get('notas') or pedido.notas or '').strip()
 
    try:
        cantidad = int(cantidad)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Cantidad invÃ¡lida'}), 400
 
    if cantidad <= 0:
        return jsonify({'success': False, 'error': 'La cantidad debe ser mayor a 0'}), 400
 
    pedido.cantidad = cantidad
    pedido.total = round(pedido.precio_unitario * cantidad, 2)
    pedido.estado = estado
    pedido.notas = notas
    db.session.commit()
 
    return jsonify({
        'success': True,
        'message': 'Pedido actualizado exitosamente',
        'pedido': pedido.to_dict()
    })
 
 

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_order(id):
    """Elimina un pedido."""
    pedido = Order.query.get(id)
    if not pedido:
        return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
 
    db.session.delete(pedido)
    db.session.commit()
 
    return jsonify({
        'success': True,
        'message': f'Pedido #{id} eliminado correctamente'
    })
 
