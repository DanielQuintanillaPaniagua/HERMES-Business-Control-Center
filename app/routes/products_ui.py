from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('products_ui', __name__, url_prefix='/products')


@bp.route('/')
@login_required
def list_page():
    """Página de listado de productos."""
    return render_template('products/list.html')


@bp.route('/new')
@login_required
def create_page():
    """Página de creación de producto."""
    return render_template('products/form.html', producto_id=None)


@bp.route('/<int:id>')
@login_required
def detail_page(id):
    """Página de detalle de un producto."""
    return render_template('products/detail.html', producto_id=id)


@bp.route('/<int:id>/edit')
@login_required
def edit_page(id):
    """Página de edición de un producto."""
    return render_template('products/form.html', producto_id=id)