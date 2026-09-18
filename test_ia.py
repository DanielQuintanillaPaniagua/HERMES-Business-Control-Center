# test_ia.py
# Script temporal para probar la IA de HERMES

from app import create_app
from app.services.gemini import preguntar_a_gemini

app = create_app()

with app.app_context():
    preguntas = [
        "¿Cuánto le debo a los proveedores?",
        "¿Qué pedidos están atrasados?",
        "¿Qué productos tienen stock bajo?",
        "¿Quiénes son mis mejores clientes?",
    ]

    for pregunta in preguntas:
        print("\n" + "=" * 70)
        print(f"❓ {pregunta}")
        print("=" * 70)
        respuesta = preguntar_a_gemini(pregunta)
        print(f"🤖 {respuesta}")
