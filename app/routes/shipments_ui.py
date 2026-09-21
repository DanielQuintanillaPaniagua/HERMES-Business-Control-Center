from flask import Blueprint, render_template

shipments_ui = Blueprint("shipments_ui", __name__, url_prefix="/shipments")


@shipments_ui.route("/")
def list_shipments():
    """Listado de envíos."""
    return render_template("shipments/list.html")


@shipments_ui.route("/new")
def new_shipment():
    """Formulario de alta."""
    return render_template("shipments/form.html", modo="crear", shipment_id=None)


@shipments_ui.route("/<int:shipment_id>")
def shipment_detail(shipment_id):
    """Detalle de un envío."""
    return render_template("shipments/detail.html", shipment_id=shipment_id)


@shipments_ui.route("/<int:shipment_id>/edit")
def edit_shipment(shipment_id):
    """Formulario de edición."""
    return render_template("shipments/form.html", modo="editar", shipment_id=shipment_id)