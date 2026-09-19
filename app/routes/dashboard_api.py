<<<<<<< HEAD
from flask import Blueprint, jsonify
from flask_login import login_required
from datetime import datetime, timedelta
import random

# ⚠️ TEMPORAL: esto simula las APIs que prometió Daniel
# (/api/dashboard/stats, /sales-chart, /alerts, /activities) mientras las sube de verdad.
# Cuando él suba su app/routes/dashboard_api.py real, BORRA este archivo
# y usa el suyo — no deben coexistir los dos con el mismo nombre.
=======
from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.services.analytics import (
    get_dashboard_stats,
    get_sales_chart_data,
    get_alerts
)
>>>>>>> origin/daniel-backend

bp = Blueprint('dashboard_api', __name__, url_prefix='/api/dashboard')


<<<<<<< HEAD
@bp.route('/stats')
@login_required
def stats():
    return jsonify({
        "success": True,
        "stats": {
            "clientes": 1254,     "cambio_clientes": 12.5,
            "proveedores": 48,    "cambio_proveedores": 4.2,
            "productos": 312,     "cambio_productos": 6.8,
            "pedidos": 3240,      "cambio_pedidos": 8.7,
            "envios": 428,        "cambio_envios": 3.6,
            "ingresos": 24780.00, "cambio_ingresos": 15.8,
        }
    })


@bp.route('/sales-chart')
@login_required
def sales_chart():
    from flask import request
    dias = int(request.args.get('dias', 30))
    hoy = datetime.now()
    labels = [(hoy - timedelta(days=i)).strftime('%d/%m') for i in range(dias - 1, -1, -1)]

    valores = []
    base = 8000
    for _ in range(dias):
        base += random.uniform(-800, 1400)
        valores.append(round(max(base, 1000), 2))

    return jsonify({
        "success": True,
        "labels": labels,
        "valores": valores,
        "pedidos_por_estado": {
            "completado": 1587,
            "pendiente": 680,
            "atrasado": 890,
            "cancelado": 103,
        }
    })


@bp.route('/alerts')
@login_required
def alerts():
    return jsonify({
        "success": True,
        "alerts": [
            {"tipo": "danger",  "mensaje": "7 pedidos atrasados", "url": "#"},
            {"tipo": "warning", "mensaje": "3 envíos requieren atención", "url": "#"},
            {"tipo": "info",    "mensaje": "5 correos sin leer", "url": "#"},
        ]
    })


@bp.route('/activities')
@login_required
def activities():
    return jsonify({
        "success": True,
        "activities": [
            {"tipo": "pedido", "texto": "Pedido #1024 realizado", "tiempo": "Hace 10 min"},
            {"tipo": "correo", "texto": "Nuevo correo de veritas@proveedor.com", "tiempo": "Hace 25 min"},
            {"tipo": "envio",  "texto": "Envío #ENV-1023 marcado como entregado", "tiempo": "Hace 1 hora"},
        ]
    })
=======
# ESTADÍSTICAS GENERALES
# GET /api/dashboard/stats
@bp.route('/stats', methods=['GET'])
@login_required
def stats():
    """Devuelve las métricas principales del dashboard."""
    try:
        datos = get_dashboard_stats()
        return jsonify({'success': True, **datos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# GRÁFICA DE VENTAS
# GET /api/dashboard/sales-chart?dias=30
@bp.route('/sales-chart', methods=['GET'])
@login_required
def sales_chart():
    """Devuelve los datos de la gráfica de ventas por día."""
    try:
        dias = int(request.args.get('dias', 30))
        datos = get_sales_chart_data(dias=dias)
        return jsonify({'success': True, **datos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ALERTAS DEL NEGOCIO
# GET /api/dashboard/alerts
@bp.route('/alerts', methods=['GET'])
@login_required
def alerts():
    """Devuelve las alertas activas (pedidos atrasados, deudas, stock bajo)."""
    try:
        alertas = get_alerts()
        return jsonify({'success': True, 'alertas': alertas, 'total': len(alertas)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
>>>>>>> origin/daniel-backend
