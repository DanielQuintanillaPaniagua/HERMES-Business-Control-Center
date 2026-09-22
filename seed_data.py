# seed_data.py
# Script para poblar la BD con datos de prueba realistas para HERMES

import random
from datetime import datetime, timedelta, date
from app import create_app, db
from app.models.user import User
from app.models.client import Client
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.order import Order
from app.models.shipment import Shipment
from app.models.invoice import Invoice


# ============================================
# DATOS DE PRUEBA
# ============================================

CLIENTES = [
    {"nombre": "Distribuidora Lopez", "email": "contacto@distlopez.com", "telefono": "+503 2222 1111", "ciudad": "San Salvador"},
    {"nombre": "Comercial Rivera", "email": "ventas@crivera.com", "telefono": "+503 2222 2222", "ciudad": "Santa Ana"},
    {"nombre": "Supermercado El Sol", "email": "info@elsol.com", "telefono": "+503 2222 3333", "ciudad": "San Miguel"},
    {"nombre": "Tiendas Unidas", "email": "pedidos@tunidas.com", "telefono": "+503 2222 4444", "ciudad": "La Libertad"},
    {"nombre": "Inversiones M&V", "email": "gerencia@myv.com", "telefono": "+503 2222 5555", "ciudad": "San Salvador"},
    {"nombre": "Grupo Comercial Azteca", "email": "compras@azteca.com", "telefono": "+503 2222 6666", "ciudad": "Sonsonate"},
    {"nombre": "Importadora Centroamericana", "email": "contacto@importca.com", "telefono": "+503 2222 7777", "ciudad": "San Salvador"},
    {"nombre": "Distribuidora del Pacifico", "email": "info@distpacifico.com", "telefono": "+503 2222 8888", "ciudad": "La Union"},
    {"nombre": "Almacenes Central", "email": "ventas@acental.com", "telefono": "+503 2222 9999", "ciudad": "San Salvador"},
    {"nombre": "Comercial La Estrella", "email": "admin@laestrella.com", "telefono": "+503 2222 0000", "ciudad": "Chalatenango"},
]

PROVEEDORES = [
    {"nombre": "Importadora XYZ", "contacto": "Juan Perez", "email": "juan@importxyz.com", "telefono": "+503 3333 1111", "direccion": "Zona Industrial, San Salvador", "saldo_pendiente": 4200.00},
    {"nombre": "ABC Logistics", "contacto": "Maria Gomez", "email": "maria@abclog.com", "telefono": "+503 3333 2222", "direccion": "Av. Independencia, Santa Ana", "saldo_pendiente": 3850.00},
    {"nombre": "Pack & Ship", "contacto": "Roberto Diaz", "email": "roberto@packship.com", "telefono": "+503 3333 3333", "direccion": "Blvd. Los Heroes, San Salvador", "saldo_pendiente": 2650.00},
    {"nombre": "Suministros Globales", "contacto": "Luis Ramirez", "email": "luis@sumglobal.com", "telefono": "+503 3333 4444", "direccion": "Calle Arce, San Salvador", "saldo_pendiente": 2190.00},
    {"nombre": "Tecnologia y Mas", "contacto": "Carla Mejia", "email": "carla@tecmas.com", "telefono": "+503 3333 5555", "direccion": "Col. Escalon, San Salvador", "saldo_pendiente": 1930.00},
    {"nombre": "Distribuidora del Norte", "contacto": "Ana Flores", "email": "ana@distnorte.com", "telefono": "+503 3333 6666", "direccion": "Metapan, Santa Ana", "saldo_pendiente": 0.00},
    {"nombre": "Comercial El Roble", "contacto": "Pedro Castillo", "email": "pedro@elroble.com", "telefono": "+503 3333 7777", "direccion": "Usulutan", "saldo_pendiente": 750.00},
    {"nombre": "Importaciones del Sur", "contacto": "Sofia Martinez", "email": "sofia@impsur.com", "telefono": "+503 3333 8888", "direccion": "San Miguel", "saldo_pendiente": 0.00},
]

PRODUCTOS = [
    {"nombre": "Laptop HP Pavilion 15", "sku": "HP-PAV15-001", "precio": 899.99, "stock": 25, "categoria": "Electronica", "descripcion": "Laptop 15.6, i5, 8GB RAM"},
    {"nombre": "Monitor LG 24 pulgadas", "sku": "LG-MON24-002", "precio": 179.99, "stock": 42, "categoria": "Electronica", "descripcion": "Monitor Full HD IPS"},
    {"nombre": "Teclado Logitech K380", "sku": "LOG-K380-003", "precio": 39.99, "stock": 8, "categoria": "Accesorios", "descripcion": "Teclado inalambrico Bluetooth"},
    {"nombre": "Mouse Inalambrico Logitech", "sku": "LOG-M185-004", "precio": 24.99, "stock": 65, "categoria": "Accesorios", "descripcion": "Mouse optico inalambrico"},
    {"nombre": "Impresora Epson EcoTank", "sku": "EPS-ET2400-005", "precio": 249.99, "stock": 5, "categoria": "Impresion", "descripcion": "Impresora multifuncional"},
    {"nombre": "Papel Bond Carta 500 hojas", "sku": "PAP-CART-006", "precio": 8.99, "stock": 120, "categoria": "Papeleria", "descripcion": "Resma de papel bond blanco"},
    {"nombre": "Boligrafo Bic Azul (x12)", "sku": "BIC-AZUL-007", "precio": 4.99, "stock": 200, "categoria": "Papeleria", "descripcion": "Caja de 12 boligrafos"},
    {"nombre": "Cuaderno Universitario", "sku": "CUAD-UNIV-008", "precio": 2.50, "stock": 150, "categoria": "Papeleria", "descripcion": "Cuaderno 100 hojas"},
    {"nombre": "Silla Ergonomic a Oficina", "sku": "SILL-ERG-009", "precio": 189.99, "stock": 12, "categoria": "Mobiliario", "descripcion": "Silla con soporte lumbar"},
    {"nombre": "Escritorio Ejecutivo", "sku": "ESCR-EJEC-010", "precio": 349.99, "stock": 6, "categoria": "Mobiliario", "descripcion": "Escritorio de madera 1.5m"},
    {"nombre": "Archivador Metalico", "sku": "ARCH-MET-011", "precio": 89.99, "stock": 18, "categoria": "Mobiliario", "descripcion": "Archivador de 4 gavetas"},
    {"nombre": "Disco Duro Externo 1TB", "sku": "HDD-EXT1TB-012", "precio": 59.99, "stock": 35, "categoria": "Electronica", "descripcion": "Disco externo USB 3.0"},
    {"nombre": "Memoria USB 64GB", "sku": "USB-64GB-013", "precio": 12.99, "stock": 9, "categoria": "Electronica", "descripcion": "Pendrive USB 3.0"},
    {"nombre": "Calculadora Cientifica", "sku": "CALC-CIEN-014", "precio": 19.99, "stock": 45, "categoria": "Papeleria", "descripcion": "Calculadora cientifica"},
    {"nombre": "Grapadora Metalica", "sku": "GRAP-MET-015", "precio": 6.99, "stock": 80, "categoria": "Papeleria", "descripcion": "Grapadora estandar"},
]

ESTADOS_PEDIDO = ["pendiente", "pendiente", "pendiente", "completado", "completado", "completado", "atrasado", "cancelado"]
ESTADOS_ENVIO = ["preparando", "en transito", "en transito", "entregado", "entregado", "entregado", "atrasado"]
TRANSPORTISTAS = ["DHL Express", "FedEx", "UPS", "Correos de El Salvador", "Transportes Rivera"]


# ============================================
# FUNCIONES DE POBLADO
# ============================================

def limpiar_datos():
    print("Limpiando datos antiguos...")
    Invoice.query.delete()
    Shipment.query.delete()
    Order.query.delete()
    Product.query.delete()
    Supplier.query.delete()
    Client.query.delete()
    db.session.commit()


def crear_clientes():
    print(f"Creando {len(CLIENTES)} clientes...")
    for c in CLIENTES:
        db.session.add(Client(**c, estado="Activo"))
    db.session.commit()


def crear_proveedores():
    print(f"Creando {len(PROVEEDORES)} proveedores...")
    for p in PROVEEDORES:
        db.session.add(Supplier(**p, estado="Activo"))
    db.session.commit()


def crear_productos():
    print(f"Creando {len(PRODUCTOS)} productos...")
    for p in PRODUCTOS:
        db.session.add(Product(**p, estado="Activo"))
    db.session.commit()


def crear_pedidos(num=25):
    print(f"Creando {num} pedidos...")
    clientes = Client.query.all()
    productos = Product.query.all()
    for _ in range(num):
        cliente = random.choice(clientes)
        producto = random.choice(productos)
        cantidad = random.randint(1, 10)
        total = round(cantidad * producto.precio, 2)
        fecha = datetime.utcnow() - timedelta(days=random.randint(0, 30))
        db.session.add(Order(
            cliente_id=cliente.id, producto_id=producto.id,
            cantidad=cantidad, precio_unitario=producto.precio,
            total=total, estado=random.choice(ESTADOS_PEDIDO),
            notas=f"Pedido de {producto.nombre}", created_at=fecha
        ))
    db.session.commit()


def crear_envios():
    print("Creando envios...")
    pedidos = Order.query.filter(Order.estado != "cancelado").all()
    pedidos_con_envio = random.sample(pedidos, k=min(20, len(pedidos)))
    for pedido in pedidos_con_envio:
        db.session.add(Shipment(
            pedido_id=pedido.id,
            direccion_envio=f"Col. Centro, {pedido.cliente.ciudad or 'San Salvador'}",
            ciudad=pedido.cliente.ciudad or "San Salvador",
            transportista=random.choice(TRANSPORTISTAS),
            numero_guia=f"GR-{random.randint(100000, 999999)}",
            estado=random.choice(ESTADOS_ENVIO),
            fecha_envio=pedido.created_at + timedelta(days=1),
            fecha_entrega_estimada=pedido.created_at + timedelta(days=random.randint(2, 10)),
            created_at=pedido.created_at
        ))
    db.session.commit()


def crear_facturas(num=15):
    print(f"Creando {num} facturas...")
    clientes = Client.query.all()
    if not clientes:
        print("No hay clientes para asignar facturas")
        return

    conceptos = [
        "Compra de insumos tecnologicos", "Servicio de instalacion de red",
        "Venta de productos varios", "Equipos de oficina",
        "Consultoria en sistemas", "Material de red y cableado",
        "Licencias de software", "Mantenimiento de servidores",
        "Servicios de internet", "Desarrollo de aplicacion",
        "Suministros de papeleria", "Mobiliario de oficina",
        "Reparacion de equipos", "Soporte tecnico anual",
        "Capacitacion de personal",
    ]
    estados = ["Pagada", "Pagada", "Pagada", "Pendiente", "Pendiente", "Vencida"]

    for i in range(1, num + 1):
        cliente = random.choice(clientes)
        numero = f"F-{100 + i:05d}"
        fecha_emision = date.today() - timedelta(days=random.randint(5, 60))
        fecha_vencimiento = fecha_emision + timedelta(days=30)
        db.session.add(Invoice(
            numero=numero, client_id=cliente.id,
            concepto=random.choice(conceptos),
            total=round(random.uniform(200, 5000), 2),
            fecha_emision=fecha_emision,
            fecha_vencimiento=fecha_vencimiento,
            estado=random.choice(estados)
        ))
    db.session.commit()


# ============================================
# MAIN
# ============================================

def main():
    app = create_app()
    with app.app_context():
        print("\n" + "=" * 60)
        print("POBLANDO BASE DE DATOS DE HERMES")
        print("=" * 60 + "\n")

        limpiar_datos()
        crear_clientes()
        crear_proveedores()
        crear_productos()
        crear_pedidos(num=25)
        crear_envios()
        crear_facturas(num=15)

        print("\n" + "=" * 60)
        print("BASE DE DATOS POBLADA EXITOSAMENTE")
        print("=" * 60)
        print(f"   Clientes:      {Client.query.count()}")
        print(f"   Proveedores:   {Supplier.query.count()}")
        print(f"   Productos:     {Product.query.count()}")
        print(f"   Pedidos:       {Order.query.count()}")
        print(f"   Envios:        {Shipment.query.count()}")
        print(f"   Facturas:      {Invoice.query.count()}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
