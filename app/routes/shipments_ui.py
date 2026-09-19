from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('shipments_ui', __name__, url_prefix='/shipments')


@bp.route('/')
@login_required
def list_page():
    """Página de listado de envíos."""
    return render_template('shipments/list.html')


@bp.route('/new')
@login_required
def create_page():
    """Página de creación de envío."""
    return render_template('shipments/form.html', envio_id=None)


@bp.route('/<int:id>')
@login_required
def detail_page(id):
    """Página de detalle de un envío."""
    return render_template('shipments/detail.html', envio_id=id)


@bp.route('/<int:id>/edit')
@login_required
def edit_page(id):
    """Página de edición de un envío."""
    return render_template('shipments/form.html', envio_id=id)