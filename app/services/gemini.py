import os
import google.generativeai as genai
from datetime import datetime
from sqlalchemy import func
from app import db
from app.models.client import Client
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.order import Order
from app.models.shipment import Shipment


# Configuración del modelo de Gemini
MODEL_NAME = "gemini-2.5-flash"

def _get_model():
    """Crea el modelo de Gemini con la API key del .env."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY no configurada en el .env")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(MODEL_NAME)


def _recopilar_contexto():
    """Recopila un resumen de los datos del negocio para dárselos a Gemini."""

    # Totales generales
    total_clientes = Client.query.count()
    total_proveedores = Supplier.query.count()
    total_productos = Product.query.count()
    total_pedidos = Order.query.count()
    total_envios = Shipment.query.count()

    # Deuda a proveedores
    deuda_total = db.session.query(
        func.coalesce(func.sum(Supplier.saldo_pendiente), 0.0)
    ).scalar()

    # Proveedores con deuda (top 5)
    proveedores_deuda = Supplier.query.filter(
        Supplier.saldo_pendiente > 0
    ).order_by(Supplier.saldo_pendiente.desc()).limit(5).all()

    proveedores_info = "\n".join([
        f"  - {p.nombre}: ${p.saldo_pendiente:.2f}"
        for p in proveedores_deuda
    ]) or "  - Ninguno"

    # Ingresos del mes
    hoy = datetime.utcnow()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ingresos_mes = db.session.query(
        func.coalesce(func.sum(Order.total), 0.0)
    ).filter(Order.created_at >= inicio_mes).scalar()

    # Pedidos por estado
    estados = db.session.query(
        Order.estado, func.count(Order.id)
    ).group_by(Order.estado).all()
    estados_info = "\n".join([f"  - {e}: {c}" for e, c in estados]) or "  - Sin pedidos"

    # Pedidos atrasados (con detalles)
    pedidos_atrasados = Order.query.filter(
        Order.estado.in_(['atrasado', 'Atrasado'])
    ).limit(10).all()

    atrasados_info = "\n".join([
        f"  - Pedido #{p.id} de {p.cliente.nombre if p.cliente else '?'}: ${p.total:.2f}"
        for p in pedidos_atrasados
    ]) or "  - Ninguno"

    # Productos con stock bajo
    stock_bajo = Product.query.filter(Product.stock < 10).all()
    stock_info = "\n".join([
        f"  - {p.nombre}: {p.stock} unidades (SKU: {p.sku})"
        for p in stock_bajo
    ]) or "  - Ninguno"

    # Top 5 clientes por pedidos
    top_clientes = db.session.query(
        Client.nombre,
        func.count(Order.id).label("total_pedidos"),
        func.coalesce(func.sum(Order.total), 0.0).label("total_compras")
    ).join(Order, Order.cliente_id == Client.id).group_by(
        Client.id, Client.nombre
    ).order_by(func.sum(Order.total).desc()).limit(5).all()

    top_clientes_info = "\n".join([
        f"  - {nombre}: {total_pedidos} pedidos, ${total_compras:.2f}"
        for nombre, total_pedidos, total_compras in top_clientes
    ]) or "  - Sin datos"

    contexto = f"""
DATOS ACTUALES DEL NEGOCIO (usar SOLO esta información):

📊 RESUMEN GENERAL:
- Total clientes: {total_clientes}
- Total proveedores: {total_proveedores}
- Total productos: {total_productos}
- Total pedidos: {total_pedidos}
- Total envíos: {total_envios}

💰 FINANZAS:
- Deuda total a proveedores: ${deuda_total:.2f}
- Ingresos del mes actual: ${ingresos_mes:.2f}

🚚 PROVEEDORES CON DEUDA (top 5):
{proveedores_info}

📦 PEDIDOS POR ESTADO:
{estados_info}

⚠️ PEDIDOS ATRASADOS:
{atrasados_info}

📉 PRODUCTOS CON STOCK BAJO (menos de 10):
{stock_info}

🏆 TOP 5 CLIENTES POR COMPRAS:
{top_clientes_info}
"""
    return contexto


def preguntar_a_gemini(pregunta_usuario):
    """Envía una pregunta a Gemini con el contexto del negocio."""

    try:
        modelo = _get_model()
        contexto = _recopilar_contexto()

        prompt = f"""Eres HERMES, el asistente inteligente de un sistema de gestión empresarial llamado "HERMES Business Control Center".

Tu personalidad:
- Profesional, conciso y servicial.
- Hablas en español.
- Das respuestas claras y directas.
- Usas emojis con moderación para hacer la respuesta más visual (📊, 💰, 📦, ⚠️).

REGLAS ESTRICTAS:
1. SOLO usa los datos del CONTEXTO de abajo para responder.
2. Si la pregunta no se puede responder con esos datos, dilo amablemente.
3. NUNCA inventes cifras, nombres o datos.
4. Si mencionas varias cosas, usa listas numeradas o con viñetas.
5. Sé conciso: máximo 150 palabras por respuesta.

CONTEXTO ACTUAL DEL NEGOCIO:
{contexto}

PREGUNTA DEL USUARIO:
{pregunta_usuario}

RESPUESTA:"""

        respuesta = modelo.generate_content(prompt)
        return respuesta.text

    except Exception as e:
        return f"❌ Lo siento, tuve un problema al procesar tu consulta. Error: {str(e)}"