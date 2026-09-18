from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('placeholder', __name__)

SECCIONES = {
    'proveedores': {'titulo': 'Proveedores', 'icono': 'bi-truck', 'descripcion': 'Gestión de proveedores y compras.'},
    'pedidos':     {'titulo': 'Pedidos', 'icono': 'bi-cart-fill', 'descripcion': 'Seguimiento y control de pedidos.'},
    'envios':      {'titulo': 'Envíos', 'icono': 'bi-send-fill', 'descripcion': 'Rastreo y gestión de envíos.'},
    'correos':     {'titulo': 'Correos', 'icono': 'bi-envelope-fill', 'descripcion': 'Bandeja de correos del negocio.'},
    'productos':   {'titulo': 'Productos', 'icono': 'bi-box-seam-fill', 'descripcion': 'Catálogo e inventario de productos.'},
    'facturas':    {'titulo': 'Facturas', 'icono': 'bi-file-earmark-text-fill', 'descripcion': 'Facturación electrónica.'},
    'finanzas':    {'titulo': 'Finanzas', 'icono': 'bi-cash-stack', 'descripcion': 'Estados financieros del negocio.'},
    'ajustes':     {'titulo': 'Ajustes', 'icono': 'bi-gear-fill', 'descripcion': 'Configuración general del sistema.'},
}


def _pagina(nombre):
    info = SECCIONES[nombre]
    return render_template('placeholder.html', **info)


@bp.route('/proveedores')
@login_required
def proveedores():
    return _pagina('proveedores')


@bp.route('/pedidos')
@login_required
def pedidos():
    return _pagina('pedidos')


@bp.route('/envios')
@login_required
def envios():
    return _pagina('envios')


@bp.route('/correos')
@login_required
def correos():
    return _pagina('correos')


@bp.route('/productos')
@login_required
def productos():
    return _pagina('productos')


@bp.route('/facturas')
@login_required
def facturas():
    return _pagina('facturas')


@bp.route('/finanzas')
@login_required
def finanzas():
    return _pagina('finanzas')


@bp.route('/ajustes')
@login_required
def ajustes():
    return _pagina('ajustes')