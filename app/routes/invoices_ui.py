from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('invoices_ui', __name__, url_prefix='/invoices')


@bp.route('/')
@login_required
def list_page():
    return render_template('invoices/list.html')


@bp.route('/new')
@login_required
def create_page():
    return render_template('invoices/form.html', factura_id=None)


@bp.route('/<int:id>')
@login_required
def detail_page(id):
    return render_template('invoices/detail.html', factura_id=id)


@bp.route('/<int:id>/edit')
@login_required
def edit_page(id):
    return render_template('invoices/form.html', factura_id=id)