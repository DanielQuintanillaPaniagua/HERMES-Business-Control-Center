from flask import Blueprint, jsonify
from flask_login import login_required
from datetime import datetime, timedelta
import random

# ⚠️ TEMPORAL: esto simula las APIs que prometió Daniel
# (/api/dashboard/stats, /sales-chart, /alerts) mientras las sube de verdad.
# Cuando él suba su app/routes/dashboard_api.py real, BORRA este archivo
# y usa el suyo — no deben coexistir los dos con el mismo nombre.

bp = Blueprint('dashboard_api', __name__, url_prefix='/api/dashboard')


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
    dias = 30
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