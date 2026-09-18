import os
import requests
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

bp = Blueprint('ia_hermes', __name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODELS_URL = "https://api.groq.com/openai/v1/models"

# Intentamos estos modelos en orden. Si ninguno funciona, consultamos
# directamente a Groq cuáles están disponibles con tu clave y usamos el primero.
MODELOS_PREFERIDOS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "gemma2-9b-it",
    "mixtral-8x7b-32768",
]

INSTRUCCION_SISTEMA = """Eres HERMES AI, el asistente virtual dentro del sistema HERMES Business Control Center.
Ayudas al usuario con preguntas sobre su negocio: clientes, pedidos, envíos, proveedores, productos e ingresos.
Responde en español, de forma breve, clara y profesional. Si no tienes datos reales conectados,
acláralo brevemente en vez de inventar cifras."""

# Una vez que encontramos un modelo que SÍ funciona, lo recordamos en memoria
# para no tener que probar los 6 en cada mensaje (más rápido).
_modelo_que_funciona = {"nombre": None}


@bp.route('/ia-hermes')
@login_required
def index():
    """Página del chat de IA HERMES."""
    return render_template('ia_hermes.html')


def _pedir_a_groq(api_key, modelo, mensaje):
    """Hace una petición a Groq con un modelo específico. Devuelve (resp, error_legible)."""
    resp = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": modelo,
            "messages": [
                {"role": "system", "content": INSTRUCCION_SISTEMA},
                {"role": "user", "content": mensaje},
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        },
        timeout=20,
    )
    if resp.status_code == 200:
        return resp, None

    try:
        mensaje_error = resp.json().get('error', {}).get('message', resp.text)
    except Exception:
        mensaje_error = resp.text
    return None, f"({resp.status_code}) {mensaje_error}"


def _obtener_modelo_disponible(api_key):
    """Consulta a Groq la lista real de modelos y devuelve el primero disponible."""
    try:
        resp = requests.get(
            GROQ_MODELS_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=15,
        )
        if resp.status_code == 200:
            modelos = resp.json().get("data", [])
            if modelos:
                return modelos[0]["id"]
    except Exception:
        pass
    return None


@bp.route('/api/ia-hermes/chat', methods=['POST'])
@login_required
def chat():
    """Recibe un mensaje del usuario y responde usando Groq, probando varios modelos si hace falta."""
    data = request.get_json(silent=True) or {}
    mensaje = (data.get('mensaje') or '').strip()

    if not mensaje:
        return jsonify({"success": False, "error": "Mensaje vacío"}), 400

    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        return jsonify({
            "success": False,
            "error": "Falta configurar GROQ_API_KEY en el archivo .env"
        }), 500

    errores = []

    # 0. Si ya sabemos qué modelo funcionó antes, usarlo directo (más rápido).
    if _modelo_que_funciona["nombre"]:
        try:
            resp, error = _pedir_a_groq(api_key, _modelo_que_funciona["nombre"], mensaje)
            if resp is not None:
                texto = resp.json()["choices"][0]["message"]["content"]
                return jsonify({"success": True, "respuesta": texto})
            errores.append(f"{_modelo_que_funciona['nombre']} (recordado): {error}")
            _modelo_que_funciona["nombre"] = None  # dejó de funcionar, lo olvidamos
        except Exception as e:
            errores.append(f"{_modelo_que_funciona['nombre']} (recordado): excepción {e}")
            _modelo_que_funciona["nombre"] = None

    # 1. Probar la lista de modelos preferidos, en orden.
    for modelo in MODELOS_PREFERIDOS:
        try:
            resp, error = _pedir_a_groq(api_key, modelo, mensaje)
            if resp is not None:
                _modelo_que_funciona["nombre"] = modelo
                texto = resp.json()["choices"][0]["message"]["content"]
                return jsonify({"success": True, "respuesta": texto})
            errores.append(f"{modelo}: {error}")
        except Exception as e:
            errores.append(f"{modelo}: excepción {e}")

    # 2. Si ninguno funcionó, preguntarle a Groq cuál modelo SÍ está disponible.
    modelo_real = _obtener_modelo_disponible(api_key)
    if modelo_real and modelo_real not in MODELOS_PREFERIDOS:
        try:
            resp, error = _pedir_a_groq(api_key, modelo_real, mensaje)
            if resp is not None:
                _modelo_que_funciona["nombre"] = modelo_real
                texto = resp.json()["choices"][0]["message"]["content"]
                return jsonify({"success": True, "respuesta": texto})
            errores.append(f"{modelo_real}: {error}")
        except Exception as e:
            errores.append(f"{modelo_real}: excepción {e}")

    # 3. Si de verdad nada funcionó, mostrar todos los errores para diagnosticar.
    return jsonify({
        "success": False,
        "error": "Ningún modelo de Groq respondió. Detalle:\n" + "\n".join(errores)
    }), 500