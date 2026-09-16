from itertools import count
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db 
from app.models.client import Client
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.order import Order
from app.models.shipment import Shipment

def get_dashboard_stats():

    total_clients = Client.query.count()
    total_provedores = Supplier.query.count()
    total_productos = Product.query.count()
    total_pedidos = Order.query.count()
    total_envios = Shipment.query.count()

    #deuda a proveedores
    deuda_proveedores = db.session.query(func.coalesce(func.sum(Supplier.saldo_pendiente),0.0)).scalar()
    # ingresos del mes actual
    hoy = datetime.utcnow()
    incio_mes = hoy.replace(day=1, hour=0, minute=0,second=0, microsecond=0)
    ingreso_mes = db.session.query(func.coalesce(func.sum(Order.total),0.0)).filter(Order.created_at >= incio_mes).scalar()
    #Pedidos por estado
    pedidos_por_estado = db.session.query(
        Order.estado,
        func.count(Order.id)
    ).group_by(Order.estado).all()
    pedidos_estado_dict = {estado: count for estado, count in pedidos_por_estado}

    return {
        "total_clientes": total_clients,
        "total_proveedores": total_provedores,
        "total_productos":total_productos,
        "total_pedidos":total_pedidos,
        "total_envios": total_envios,
        "deuda_proveedores": round(deuda_proveedores,2),
        "ingreso_mes": round(ingreso_mes,2),
        "pedidos_por_estado":{
            "pendiente": pedidos_estado_dict.get("pendiente",0) + pedidos_estado_dict.get("pendiente",0),
            "completados": pedidos_estado_dict.get("completado",0) + pedidos_estado_dict.get("completado",0),
            "atrasados": pedidos_estado_dict.get("atrasado",0) + pedidos_estado_dict.get("atrasado",0),
            "cancelados": pedidos_estado_dict.get("cancelado",0) + pedidos_estado_dict.get("cancelado",0)
        }
    }
def get_sales_chart_data(dias=30):
    hoy = datetime.utcnow()
    inicio = hoy - timedelta(days=days)

    ventas = db.session.query(func.date(Order.created_at).label("fecha"),func.coalesce
    (func.sum(Order.total),0.0).label("total")).filter(Order.created_at >= inicio).group_by(func.date(Order.created_at)).order_by
    (func.date(Order.created_at)).all()

    ventas_dict= {str(fecha): float(total) for fecha, total in ventas}
    labels = []
    data = []
    for i in range(days):
        dia = inicio + timedelta(days=i)
        dia_str = dia.strftime("%d/%m/%Y")
        labels.append(dia.strftime("%d/%m"))
        data.append(ventas_dict.get(dia_str,0.0))
    return {
        "labels":labels,
        "data":data
    }
def get_alerts():
    """Devuelve alertas activas del negocio."""
    
    alertas = []
    
    # 1. Proveedores con saldo pendiente
    proveedores_con_deuda = Supplier.query.filter(
        Supplier.saldo_pendiente > 0
    ).order_by(Supplier.saldo_pendiente.desc()).limit(5).all()
    
    if proveedores_con_deuda:
        alertas.append({
            'tipo': 'warning',
            'titulo': f'{len(proveedores_con_deuda)} proveedores con saldo pendiente',
            'detalle': f'Total adeudado: ${sum(p.saldo_pendiente for p in proveedores_con_deuda):.2f}',
            'items': [
                {'nombre': p.nombre, 'valor': f'${p.saldo_pendiente:.2f}'}
                for p in proveedores_con_deuda
            ]
        })
    
    # 2. Pedidos atrasados
    pedidos_atrasados = Order.query.filter_by(estado='atrasado').all()
    if not pedidos_atrasados:
        pedidos_atrasados = Order.query.filter_by(estado='Atrasado').all()
    
    if pedidos_atrasados:
        alertas.append({
            'tipo': 'danger',
            'titulo': f'{len(pedidos_atrasados)} pedidos atrasados',
            'detalle': 'Requieren atenciÃ³n inmediata'
        })
    
    # 3. Productos con stock bajo (< 10)
    productos_bajo_stock = Product.query.filter(Product.stock < 10).all()
    if productos_bajo_stock:
        alertas.append({
            'tipo': 'info',
            'titulo': f'{len(productos_bajo_stock)} productos con stock bajo',
            'detalle': 'Menos de 10 unidades disponibles',
            'items': [
                {'nombre': p.nombre, 'valor': f'{p.stock} uds'}
                for p in productos_bajo_stock[:5]
            ]
        })
    
    return alertas
    
        
        
        
    
    
    
        
    


    
    

