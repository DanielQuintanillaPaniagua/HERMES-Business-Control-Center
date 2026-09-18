from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.services.gemini import preguntar_a_gemini

bp = Blueprint("ai_api", __name__, url_prefix="/api/ai")


@bp.route("/ask", methods=["POST"])
@login_required
def ask():
    """Recibe una pregunta del usuario y devuelve la respuesta de Gemini."""
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "No se enviaron datos"}), 400

    pregunta = (data.get("pregunta") or "").strip()

    if not pregunta:
        return jsonify({"success": False, "error": "La pregunta no puede estar vacía"}), 400

    if len(pregunta) > 500:
        return jsonify({"success": False, "error": "La pregunta es demasiado larga (máximo 500 caracteres)"}), 400

    respuesta = preguntar_a_gemini(pregunta)

    return jsonify({
        "success": True,
        "pregunta": pregunta,
        "respuesta": respuesta
    })