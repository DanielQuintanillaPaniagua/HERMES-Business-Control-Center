from flask import Blueprint, request, jsonify
from flask_login import login_required
from app import db
from app.models.product import Product

bp = Blueprint('products', __name__, url_prefix='/api/products')

 
# LISTAR: GET /api/products
@bp.route('/', methods=['GET'])
@login_required
def list_products():
    """Devuelve la lista de todos los productos."""
    productos = Product.query.order_by(Product.nombre).all()
    return jsonify({
        'success': True,
        'total': len(productos),
        'productos': [p.to_dict() for p in productos]
    })



# VER UNO: GET /api/products/<id>

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_product(id):
    """Devuelve un producto especÃ­fico."""
    producto = Product.query.get(id)
    if not producto:
        return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
    return jsonify({'success': True, 'producto': producto.to_dict()})



# CREAR: POST /api/products

@bp.route('/', methods=['POST'])
@login_required
def create_product():
    """Crea un nuevo producto."""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400

    nombre = (data.get('nombre') or '').strip()
    sku = (data.get('sku') or '').strip().upper()
    descripcion = (data.get('descripcion') or '').strip()
    precio = data.get('precio', 0.0)
    stock = data.get('stock', 0)
    categoria = (data.get('categoria') or '').strip()

    if not nombre or not sku:
        return jsonify({'success': False, 'error': 'Nombre y SKU son obligatorios'}), 400

    if Product.query.filter_by(sku=sku).first():
        return jsonify({'success': False, 'error': 'Ese SKU ya estÃ¡ registrado'}), 409

    try:
        precio = float(precio)
        stock = int(stock)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Precio o stock invÃ¡lidos'}), 400

    if precio < 0 or stock < 0:
        return jsonify({'success': False, 'error': 'Precio y stock deben ser positivos'}), 400

    producto = Product(
        nombre=nombre,
        sku=sku,
        descripcion=descripcion,
        precio=precio,
        stock=stock,
        categoria=categoria,
        estado='Activo'
    )
    db.session.add(producto)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Producto "{nombre}" creado exitosamente',
        'producto': producto.to_dict()
    }), 201



# EDITAR: PUT /api/products/<id>
@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_product(id):
    """Actualiza un producto existente."""
    producto = Product.query.get(id)
    if not producto:
        return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400

    nombre = (data.get('nombre') or producto.nombre).strip()
    sku = (data.get('sku') or producto.sku).strip().upper()
    descripcion = (data.get('descripcion') or '').strip()
    categoria = (data.get('categoria') or '').strip()
    estado = data.get('estado', producto.estado)

    if not nombre or not sku:
        return jsonify({'success': False, 'error': 'Nombre y SKU son obligatorios'}), 400

    existente = Product.query.filter_by(sku=sku).first()
    if existente and existente.id != id:
        return jsonify({'success': False, 'error': 'Ese SKU ya estÃ¡ en uso'}), 409

    try:
        precio = float(data.get('precio', producto.precio))
        stock = int(data.get('stock', producto.stock))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Precio o stock invÃ¡lidos'}), 400

    if precio < 0 or stock < 0:
        return jsonify({'success': False, 'error': 'Precio y stock deben ser positivos'}), 400

    producto.nombre = nombre
    producto.sku = sku
    producto.descripcion = descripcion
    producto.precio = precio
    producto.stock = stock
    producto.categoria = categoria
    producto.estado = estado
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Producto actualizado exitosamente',
        'producto': producto.to_dict()
    })



# ELIMINAR: DELETE /api/products/<id>

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_product(id):
    """Elimina un producto."""
    producto = Product.query.get(id)
    if not producto:
        return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

    nombre = producto.nombre
    db.session.delete(producto)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Producto "{nombre}" eliminado correctamente'
    })
