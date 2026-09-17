from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@login_required
def index():
    """Página principal de HERMES tras iniciar sesión."""

    # TODO: reemplazar por queries reales cuando existan los modelos
    return render_template(
        'dashboard.html',
        total_clientes=1254, cambio_clientes=12.5,
        total_pedidos=3240, cambio_pedidos=8.7,
        total_envios=428, cambio_envios=3.6,
        ingresos_mes=24780.00, cambio_ingresos=15.8,
        ventas_labels=list(range(1, 31)),
        ventas_datos=[5000, 7000, 6500, 9000, 8700, 10000, 9500, 11000,
                      12500, 13000, 12000, 14000, 13500, 15000, 16000,
                      15500, 17000, 18000, 17500, 19000, 20000, 19500,
                      21000, 22000, 21500, 23000, 24000, 23500, 24500, 24780],
        estado_labels=["Completados", "En progreso", "Pendientes", "Cancelados"],
        estado_datos=[1587, 890, 680, 103],
        actividades_recientes=[
            {"texto": "Pedido #1024 realizado", "tiempo": "Hace 10 min"},
            {"texto": "Nuevo correo de veritas@proveedor.com", "tiempo": "Hace 25 min"},
            {"texto": "Envío #ENV-1023 marcado como entregado", "tiempo": "Hace 1 hora"},
        ],
        recordatorios=[
            {"texto": "7 pedidos atrasados", "url": "#"},
            {"texto": "3 envíos requieren atención", "url": "#"},
            {"texto": "5 correos sin leer", "url": "#"},
        ],
    )