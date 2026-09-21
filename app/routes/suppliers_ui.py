# app/routes/suppliers_ui.py
from flask import Blueprint, render_template
from flask_login import login_required

suppliers_ui = Blueprint("suppliers_ui", __name__, url_prefix="/suppliers")


@suppliers_ui.route("/")
@login_required
def list_suppliers():
    return render_template("suppliers/list.html")


@suppliers_ui.route("/new")
@login_required
def new_supplier():
    return render_template("suppliers/form.html", modo="crear", supplier_id=None)


@suppliers_ui.route("/<int:supplier_id>")
@login_required
def supplier_detail(supplier_id):
    return render_template("suppliers/detail.html", supplier_id=supplier_id)


@suppliers_ui.route("/<int:supplier_id>/edit")
@login_required
def edit_supplier(supplier_id):
    return render_template("suppliers/form.html", modo="editar", supplier_id=supplier_id)
