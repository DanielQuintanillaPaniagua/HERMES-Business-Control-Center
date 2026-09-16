from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('clients_ui', __name__, url_prefix='/clients')


@bp.route('/')
@login_required
def list_page():
    """Página de listado de clientes."""
    return render_template('clients/list.html')


@bp.route('/new')
@login_required
def create_page():
    """Página de creación de cliente."""
    return render_template('clients/form.html', cliente_id=None)


@bp.route('/<int:id>')
@login_required
def detail_page(id):
    """Página de detalle de un cliente."""
    return render_template('clients/detail.html', cliente_id=id)


@bp.route('/<int:id>/edit')
@login_required
def edit_page(id):
    """Página de edición de un cliente."""
    return render_template('clients/form.html', cliente_id=id)