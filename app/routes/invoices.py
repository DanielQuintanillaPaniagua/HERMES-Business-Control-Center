from flask import Blueprint, request, jsonify, make_response
from flask_login import login_required
from datetime import datetime, date
import json
from app import db
from app.models.invoice import Invoice
from app.models.client import Client

bp = Blueprint('invoices', __name__, url_prefix='/api/invoices')


# ============================================
# LISTAR
# ============================================
@bp.route('/', methods=['GET'])
@login_required
def list_invoices():
    facturas = Invoice.query.order_by(Invoice.fecha_emision.desc()).all()
    return jsonify({
        'success': True,
        'total': len(facturas),
        'facturas': [f.to_dict() for f in facturas]
    })


# ============================================
# VER UNO
# ============================================
@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_invoice(id):
    factura = Invoice.query.get(id)
    if not factura:
        return jsonify({'success': False, 'error': 'Factura no encontrada'}), 404
    return jsonify({'success': True, 'factura': factura.to_dict()})


# ============================================
# CREAR
# ============================================
@bp.route('/', methods=['POST'])
@login_required
def create_invoice():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400

    numero = (data.get('numero') or '').strip()
    client_id = data.get('client_id')
    concepto = (data.get('concepto') or '').strip()
    total = data.get('total', 0.0)
    fecha_emision_str = data.get('fecha_emision')
    fecha_vencimiento_str = data.get('fecha_vencimiento')
    estado = data.get('estado', 'Pendiente')

    if not numero or not client_id or not concepto:
        return jsonify({'success': False, 'error': 'Numero, cliente y concepto son obligatorios'}), 400

    if Invoice.query.filter_by(numero=numero).first():
        return jsonify({'success': False, 'error': 'Ese numero de factura ya existe'}), 409

    try:
        fecha_emision = datetime.strptime(fecha_emision_str, '%Y-%m-%d').date() if fecha_emision_str else date.today()
        fecha_vencimiento = datetime.strptime(fecha_vencimiento_str, '%Y-%m-%d').date() if fecha_vencimiento_str else date.today()
        total = float(total)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Fechas o total invalidos'}), 400

    factura = Invoice(
        numero=numero, client_id=client_id, concepto=concepto,
        total=total, fecha_emision=fecha_emision,
        fecha_vencimiento=fecha_vencimiento, estado=estado
    )
    db.session.add(factura)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Factura {numero} creada',
        'factura': factura.to_dict()
    }), 201


# ============================================
# ACTUALIZAR
# ============================================
@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_invoice(id):
    factura = Invoice.query.get(id)
    if not factura:
        return jsonify({'success': False, 'error': 'Factura no encontrada'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400

    numero = (data.get('numero') or factura.numero).strip()
    client_id = data.get('client_id', factura.client_id)
    concepto = (data.get('concepto') or factura.concepto).strip()
    total = data.get('total', factura.total)
    estado = data.get('estado', factura.estado)

    existente = Invoice.query.filter_by(numero=numero).first()
    if existente and existente.id != id:
        return jsonify({'success': False, 'error': 'Ese numero ya esta en uso'}), 409

    try:
        if data.get('fecha_emision'):
            factura.fecha_emision = datetime.strptime(data['fecha_emision'], '%Y-%m-%d').date()
        if data.get('fecha_vencimiento'):
            factura.fecha_vencimiento = datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d').date()
        total = float(total)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Datos invalidos'}), 400

    factura.numero = numero
    factura.client_id = client_id
    factura.concepto = concepto
    factura.total = total
    factura.estado = estado
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Factura actualizada',
        'factura': factura.to_dict()
    })


# ============================================
# ELIMINAR
# ============================================
@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_invoice(id):
    factura = Invoice.query.get(id)
    if not factura:
        return jsonify({'success': False, 'error': 'Factura no encontrada'}), 404

    numero = factura.numero
    db.session.delete(factura)
    db.session.commit()

    return jsonify({'success': True, 'message': f'Factura {numero} eliminada'})


# ============================================
# DESCARGA JSON
# ============================================
@bp.route('/<int:id>/download/json', methods=['GET'])
@login_required
def download_json(id):
    factura = Invoice.query.get(id)
    if not factura:
        return jsonify({'success': False, 'error': 'Factura no encontrada'}), 404

    data = factura.to_dict()
    response = make_response(json.dumps(data, indent=2, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename=factura_{factura.numero}.json'
    return response


# ============================================
# DESCARGA PDF
# ============================================
@bp.route('/<int:id>/download/pdf', methods=['GET'])
@login_required
def download_pdf(id):
    from app.services.pdf_service import generar_pdf_factura

    factura = Invoice.query.get(id)
    if not factura:
        return jsonify({'success': False, 'error': 'Factura no encontrada'}), 404

    try:
        pdf_bytes = generar_pdf_factura(factura)
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=factura_{factura.numero}.pdf'
        return response
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error generando PDF: {str(e)}'}), 500