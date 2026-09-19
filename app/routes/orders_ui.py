from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('orders_ui', __name__, url_prefix='/orders')


@bp.route('/')
@login_required
def list_page():
    """Página de listado de pedidos."""
    return render_template('orders/list.html')


@bp.route('/new')
@login_required
def create_page():
    """Página de creación de pedido."""
    return render_template('orders/form.html', pedido_id=None)


@bp.route('/<int:id>')
@login_required
def detail_page(id):
    """Página de detalle de un pedido."""
    return render_template('orders/detail.html', pedido_id=id)


@bp.route('/<int:id>/edit')
@login_required
def edit_page(id):
    """Página de edición de un pedido."""
    return render_template('orders/form.html', pedido_id=id)
