# app/services/analytics.py

from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models.client import Client
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.order import Order
from app.models.shipment import Shipment


def _calcular_cambio_mes_actual(modelo):
    hoy = datetime.utcnow()
    inicio_mes_actual = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total_actual = modelo.query.filter(modelo.created_at >= inicio_mes_actual).count()
    fin_mes_pasado = inicio_mes_actual - timedelta(seconds=1)
    inicio_mes_pasado = fin_mes_pasado.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total_pasado = modelo.query.filter(
        modelo.created_at >= inicio_mes_pasado,
        modelo.created_at <= fin_mes_pasado
    ).count()
    if total_pasado == 0:
        return 100.0 if total_actual > 0 else 0.0
    return round(((total_actual - total_pasado) / total_pasado) * 100, 1)


def get_dashboard_stats():
    total_clientes = Client.query.count()
    total_proveedores = Supplier.query.count()
    total_productos = Product.query.count()
    total_pedidos = Order.query.count()
    total_envios = Shipment.query.count()

    deuda_proveedores = db.session.query(
        func.coalesce(func.sum(Supplier.saldo_pendiente), 0.0)
    ).scalar()

    hoy = datetime.utcnow()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ingresos_mes = db.session.query(
        func.coalesce(func.sum(Order.total), 0.0)
    ).filter(Order.created_at >= inicio_mes).scalar()

    pedidos_por_estado = db.session.query(
        Order.estado, func.count(Order.id)
    ).group_by(Order.estado).all()
    pedidos_estado_dict = {estado: cnt for estado, cnt in pedidos_por_estado}

    return {
        "total_clientes": total_clientes,
        "total_proveedores": total_proveedores,
        "total_productos": total_productos,
        "total_pedidos": total_pedidos,
        "total_envios": total_envios,
        "deuda_proveedores": round(deuda_proveedores, 2),
        "ingresos_mes": round(ingresos_mes, 2),
        "cambio_clientes": _calcular_cambio_mes_actual(Client),
        "cambio_proveedores": _calcular_cambio_mes_actual(Supplier),
        "cambio_productos": _calcular_cambio_mes_actual(Product),
        "cambio_pedidos": _calcular_cambio_mes_actual(Order),
        "cambio_envios": _calcular_cambio_mes_actual(Shipment),
        "cambio_ingresos": 0.0,
        "pedidos_por_estado": {
            "pendiente": pedidos_estado_dict.get("pendiente", 0),
            "completado": pedidos_estado_dict.get("completado", 0),
            "atrasado": pedidos_estado_dict.get("atrasado", 0),
            "cancelado": pedidos_estado_dict.get("cancelado", 0),
        }
    }


def get_sales_chart_data(dias=30):
    hoy = datetime.utcnow()
    inicio = hoy - timedelta(days=dias)
    ventas = db.session.query(
        func.date(Order.created_at).label("fecha"),
        func.coalesce(func.sum(Order.total), 0.0).label("total")
    ).filter(Order.created_at >= inicio).group_by(
        func.date(Order.created_at)
    ).order_by(func.date(Order.created_at)).all()

    ventas_dict = {str(fecha): float(total) for fecha, total in ventas}
    labels = []
    data = []
    for i in range(dias):
        dia = inicio + timedelta(days=i)
        dia_iso = dia.strftime("%Y-%m-%d")
        labels.append(dia.strftime("%d/%m/%Y"))
        data.append(ventas_dict.get(dia_iso, 0.0))

    return {"labels": labels, "data": data, "total": round(sum(data), 2)}


def get_alerts():
    alertas = []
    proveedores_con_deuda = Supplier.query.filter(
        Supplier.saldo_pendiente > 0
    ).order_by(Supplier.saldo_pendiente.desc()).limit(5).all()
    if proveedores_con_deuda:
        alertas.append({
            "tipo": "warning",
            "titulo": f"{len(proveedores_con_deuda)} proveedores con saldo pendiente",
            "detalle": f"Total adeudado: ${sum(p.saldo_pendiente for p in proveedores_con_deuda):.2f}",
            "items": [{"nombre": p.nombre, "valor": f"${p.saldo_pendiente:.2f}"} for p in proveedores_con_deuda]
        })

    pedidos_atrasados = Order.query.filter_by(estado="atrasado").all()
    if not pedidos_atrasados:
        pedidos_atrasados = Order.query.filter_by(estado="Atrasado").all()
    if pedidos_atrasados:
        alertas.append({
            "tipo": "danger",
            "titulo": f"{len(pedidos_atrasados)} pedidos atrasados",
            "detalle": "Requieren atención inmediata"
        })

    productos_bajo_stock = Product.query.filter(Product.stock < 10).all()
    if productos_bajo_stock:
        alertas.append({
            "tipo": "info",
            "titulo": f"{len(productos_bajo_stock)} productos con stock bajo",
            "detalle": "Menos de 10 unidades disponibles",
            "items": [{"nombre": p.nombre, "valor": f"{p.stock} uds"} for p in productos_bajo_stock[:5]]
        })

    return alertas
