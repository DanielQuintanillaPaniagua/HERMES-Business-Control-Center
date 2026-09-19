# seed_data.py
# Script para poblar la BD con datos de prueba realistas para HERMES

import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.client import Client
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.order import Order
from app.models.shipment import Shipment


# ============================================
# DATOS DE PRUEBA
# ============================================

CLIENTES = [
    {"nombre": "Distribuidora López", "email": "contacto@distlopez.com", "telefono": "+503 2222 1111", "ciudad": "San Salvador"},
    {"nombre": "Comercial Rivera", "email": "ventas@crivera.com", "telefono": "+503 2222 2222", "ciudad": "Santa Ana"},
    {"nombre": "Supermercado El Sol", "email": "info@elsol.com", "telefono": "+503 2222 3333", "ciudad": "San Miguel"},
    {"nombre": "Tiendas Unidas", "email": "pedidos@tunidas.com", "telefono": "+503 2222 4444", "ciudad": "La Libertad"},
    {"nombre": "Inversiones M&V", "email": "gerencia@myv.com", "telefono": "+503 2222 5555", "ciudad": "San Salvador"},
    {"nombre": "Grupo Comercial Azteca", "email": "compras@azteca.com", "telefono": "+503 2222 6666", "ciudad": "Sonsonate"},
    {"nombre": "Importadora Centroamericana", "email": "contacto@importca.com", "telefono": "+503 2222 7777", "ciudad": "San Salvador"},
    {"nombre": "Distribuidora del Pacífico", "email": "info@distpacifico.com", "telefono": "+503 2222 8888", "ciudad": "La Unión"},
    {"nombre": "Almacenes Central", "email": "ventas@acental.com", "telefono": "+503 2222 9999", "ciudad": "San Salvador"},
    {"nombre": "Comercial La Estrella", "email": "admin@laestrella.com", "telefono": "+503 2222 0000", "ciudad": "Chalatenango"},
]

PROVEEDORES = [
    {"nombre": "Importadora XYZ", "contacto": "Juan Pérez", "email": "juan@importxyz.com", "telefono": "+503 3333 1111", "direccion": "Zona Industrial, San Salvador", "saldo_pendiente": 4200.00},
    {"nombre": "ABC Logistics", "contacto": "María Gómez", "email": "maria@abclog.com", "telefono": "+503 3333 2222", "direccion": "Av. Independencia, Santa Ana", "saldo_pendiente": 3850.00},
    {"nombre": "Pack & Ship", "contacto": "Roberto Díaz", "email": "roberto@packship.com", "telefono": "+503 3333 3333", "direccion": "Blvd. Los Héroes, San Salvador", "saldo_pendiente": 2650.00},
    {"nombre": "Suministros Globales", "contacto": "Luis Ramírez", "email": "luis@sumglobal.com", "telefono": "+503 3333 4444", "direccion": "Calle Arce, San Salvador", "saldo_pendiente": 2190.00},
    {"nombre": "Tecnología y Más", "contacto": "Carla Mejía", "email": "carla@tecmas.com", "telefono": "+503 3333 5555", "direccion": "Col. Escalón, San Salvador", "saldo_pendiente": 1930.00},
    {"nombre": "Distribuidora del Norte", "contacto": "Ana Flores", "email": "ana@distnorte.com", "telefono": "+503 3333 6666", "direccion": "Metapán, Santa Ana", "saldo_pendiente": 0.00},
    {"nombre": "Comercial El Roble", "contacto": "Pedro Castillo", "email": "pedro@elroble.com", "telefono": "+503 3333 7777", "direccion": "Usulután", "saldo_pendiente": 750.00},
    {"nombre": "Importaciones del Sur", "contacto": "Sofía Martínez", "email": "sofia@impsur.com", "telefono": "+503 3333 8888", "direccion": "San Miguel", "saldo_pendiente": 0.00},
]

PRODUCTOS = [
    {"nombre": "Laptop HP Pavilion 15", "sku": "HP-PAV15-001", "precio": 899.99, "stock": 25, "categoria": "Electrónica", "descripcion": "Laptop 15.6, i5, 8GB RAM, 512GB SSD"},
    {"nombre": "Monitor LG 24 pulgadas", "sku": "LG-MON24-002", "precio": 179.99, "stock": 42, "categoria": "Electrónica", "descripcion": "Monitor Full HD IPS"},
    {"nombre": "Teclado Logitech K380", "sku": "LOG-K380-003", "precio": 39.99, "stock": 8, "categoria": "Accesorios", "descripcion": "Teclado inalámbrico Bluetooth"},
    {"nombre": "Mouse Inalámbrico Logitech", "sku": "LOG-M185-004", "precio": 24.99, "stock": 65, "categoria": "Accesorios", "descripcion": "Mouse óptico inalámbrico"},
    {"nombre": "Impresora Epson EcoTank", "sku": "EPS-ET2400-005", "precio": 249.99, "stock": 5, "categoria": "Impresión", "descripcion": "Impresora multifuncional"},
    {"nombre": "Papel Bond Carta 500 hojas", "sku": "PAP-CART-006", "precio": 8.99, "stock": 120, "categoria": "Papelería", "descripcion": "Resma de papel bond blanco"},
    {"nombre": "Bolígrafo Bic Azul (x12)", "sku": "BIC-AZUL-007", "precio": 4.99, "stock": 200, "categoria": "Papelería", "descripcion": "Caja de 12 bolígrafos"},
    {"nombre": "Cuaderno Universitario", "sku": "CUAD-UNIV-008", "precio": 2.50, "stock": 150, "categoria": "Papelería", "descripcion": "Cuaderno 100 hojas"},
    {"nombre": "Silla Ergonómica de Oficina", "sku": "SILL-ERG-009", "precio": 189.99, "stock": 12, "categoria": "Mobiliario", "descripcion": "Silla con soporte lumbar"},
    {"nombre": "Escritorio Ejecutivo", "sku": "ESCR-EJEC-010", "precio": 349.99, "stock": 6, "categoria": "Mobiliario", "descripcion": "Escritorio de madera 1.5m"},
    {"nombre": "Archivador Metálico", "sku": "ARCH-MET-011", "precio": 89.99, "stock": 18, "categoria": "Mobiliario", "descripcion": "Archivador de 4 gavetas"},
    {"nombre": "Disco Duro Externo 1TB", "sku": "HDD-EXT1TB-012", "precio": 59.99, "stock": 35, "categoria": "Electrónica", "descripcion": "Disco externo USB 3.0"},
    {"nombre": "Memoria USB 64GB", "sku": "USB-64GB-013", "precio": 12.99, "stock": 9, "categoria": "Electrónica", "descripcion": "Pendrive USB 3.0"},
    {"nombre": "Calculadora Científica", "sku": "CALC-CIEN-014", "precio": 19.99, "stock": 45, "categoria": "Papelería", "descripcion": "Calculadora científica Casio"},
    {"nombre": "Grapadora Metálica", "sku": "GRAP-MET-015", "precio": 6.99, "stock": 80, "categoria": "Papelería", "descripcion": "Grapadora estándar"},
]

ESTADOS_PEDIDO = ["pendiente", "pendiente", "pendiente", "completado", "completado", "completado", "atrasado", "cancelado"]

ESTADOS_ENVIO = ["preparando", "en transito", "en transito", "entregado", "entregado", "entregado", "atrasado"]

TRANSPORTISTAS = ["DHL Express", "FedEx", "UPS", "Correos de El Salvador", "Transportes Rivera"]


# ============================================
# FUNCIONES DE POBLADO
# ============================================

def limpiar_datos():
    """Elimina los datos de prueba existentes (excepto usuarios)."""
    print("🧹 Limpiando datos antiguos...")
    Shipment.query.delete()
    Order.query.delete()
    Product.query.delete()
    Supplier.query.delete()
    Client.query.delete()
    db.session.commit()


def crear_clientes():
    print(f"👥 Creando {len(CLIENTES)} clientes...")
    for c in CLIENTES:
        cliente = Client(**c, estado="Activo")
        db.session.add(cliente)
    db.session.commit()


def crear_proveedores():
    print(f"🚚 Creando {len(PROVEEDORES)} proveedores...")
    for p in PROVEEDORES:
        proveedor = Supplier(**p, estado="Activo")
        db.session.add(proveedor)
    db.session.commit()


def crear_productos():
    print(f"📦 Creando {len(PRODUCTOS)} productos...")
    for p in PRODUCTOS:
        producto = Product(**p, estado="Activo")
        db.session.add(producto)
    db.session.commit()


def crear_pedidos(num=25):
    print(f"🛒 Creando {num} pedidos...")
    clientes = Client.query.all()
    productos = Product.query.all()

    for _ in range(num):
        cliente = random.choice(clientes)
        producto = random.choice(productos)
        cantidad = random.randint(1, 10)
        precio_unitario = producto.precio
        total = round(cantidad * precio_unitario, 2)
        estado = random.choice(ESTADOS_PEDIDO)
        # Fecha aleatoria en los últimos 30 días
        fecha = datetime.utcnow() - timedelta(days=random.randint(0, 30))

        pedido = Order(
            cliente_id=cliente.id,
            producto_id=producto.id,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            total=total,
            estado=estado,
            notas=f"Pedido de {producto.nombre} para {cliente.nombre}",
            created_at=fecha
        )
        db.session.add(pedido)
    db.session.commit()


def crear_envios():
    print("📮 Creando envíos...")
    # Solo algunos pedidos tienen envío (los no cancelados)
    pedidos = Order.query.filter(Order.estado != "cancelado").all()
    pedidos_con_envio = random.sample(pedidos, k=min(20, len(pedidos)))

    for pedido in pedidos_con_envio:
        estado = random.choice(ESTADOS_ENVIO)
        fecha_estimada = pedido.created_at + timedelta(days=random.randint(2, 10))

        envio = Shipment(
            pedido_id=pedido.id,
            direccion_envio=f"Col. Centro, {pedido.cliente.ciudad or 'San Salvador'}",
            ciudad=pedido.cliente.ciudad or "San Salvador",
            transportista=random.choice(TRANSPORTISTAS),
            numero_guia=f"GR-{random.randint(100000, 999999)}",
            estado=estado,
            fecha_envio=pedido.created_at + timedelta(days=1),
            fecha_entrega_estimada=fecha_estimada,
            created_at=pedido.created_at
        )
        db.session.add(envio)
    db.session.commit()


# ============================================
# MAIN
# ============================================

def main():
    app = create_app()
    with app.app_context():
        print("\n" + "=" * 60)
        print("🌱 POBLANDO BASE DE DATOS DE HERMES")
        print("=" * 60 + "\n")

        limpiar_datos()
        crear_clientes()
        crear_proveedores()
        crear_productos()
        crear_pedidos(num=25)
        crear_envios()

        print("\n" + "=" * 60)
        print("✅ BASE DE DATOS POBLADA EXITOSAMENTE")
        print("=" * 60)
        print(f"   👥 Clientes:      {Client.query.count()}")
        print(f"   🚚 Proveedores:   {Supplier.query.count()}")
        print(f"   📦 Productos:     {Product.query.count()}")
        print(f"   🛒 Pedidos:       {Order.query.count()}")
        print(f"   📮 Envíos:        {Shipment.query.count()}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
