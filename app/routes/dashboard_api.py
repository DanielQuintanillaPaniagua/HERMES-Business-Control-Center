from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.services.analytics import (
    get_dashboard_stats,
    get_sales_chart_data,
    get_alerts
)

bp = Blueprint('dashboard_api', __name__, url_prefix='/api/dashboard')


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