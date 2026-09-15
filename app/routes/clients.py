from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models.client import Client

bp = Blueprint('clients', __name__, url_prefix='/clients')


@bp.route('/')
@login_required
def list():
    """Lista todos los clientes."""
    clientes = Client.query.order_by(Client.nombre).all()
    return render_template('clients/list.html', clientes=clientes)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """Crear un nuevo cliente."""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip().lower()
        telefono = request.form.get('telefono', '').strip()
        ciudad = request.form.get('ciudad', '').strip()

        # Validaciones
        if not nombre or not email:
            flash('Nombre y email son obligatorios', 'danger')
            return redirect(url_for('clients.create'))

        # Verificar email Ãºnico
        if Client.query.filter_by(email=email).first():
            flash('Ese email ya estÃ¡ registrado', 'danger')
            return redirect(url_for('clients.create'))

        # Crear cliente
        cliente = Client(
            nombre=nombre,
            email=email,
            telefono=telefono,
            ciudad=ciudad,
            estado='Activo'
        )
        db.session.add(cliente)
        db.session.commit()

        flash(f'Cliente "{nombre}" creado exitosamente', 'success')
        return redirect(url_for('clients.list'))

    return render_template('clients/form.html', cliente=None)


@bp.route('/<int:id>')
@login_required
def detail(id):
    """Ver detalle de un cliente."""
    cliente = Client.query.get_or_404(id)
    return render_template('clients/detail.html', cliente=cliente)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar un cliente existente."""
    cliente = Client.query.get_or_404(id)

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip().lower()
        telefono = request.form.get('telefono', '').strip()
        ciudad = request.form.get('ciudad', '').strip()
        estado = request.form.get('estado', 'Activo')

        if not nombre or not email:
            flash('Nombre y email son obligatorios', 'danger')
            return redirect(url_for('clients.edit', id=id))

        # Verificar email Ãºnico (excepto el propio cliente)
        existente = Client.query.filter_by(email=email).first()
        if existente and existente.id != id:
            flash('Ese email ya estÃ¡ registrado por otro cliente', 'danger')
            return redirect(url_for('clients.edit', id=id))

        cliente.nombre = nombre
        cliente.email = email
        cliente.telefono = telefono
        cliente.ciudad = ciudad
        cliente.estado = estado
        db.session.commit()

        flash('Cliente actualizado exitosamente', 'success')
        return redirect(url_for('clients.list'))

    return render_template('clients/form.html', cliente=cliente)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Eliminar un cliente."""
    cliente = Client.query.get_or_404(id)
    nombre = cliente.nombre
    db.session.delete(cliente)
    db.session.commit()

    flash(f'Cliente "{nombre}" eliminado', 'info')
    return redirect(url_for('clients.list'))
