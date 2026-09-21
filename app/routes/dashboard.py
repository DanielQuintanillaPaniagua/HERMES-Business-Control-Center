from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@login_required
def index():
    """Página principal de HERMES tras iniciar sesión."""
    return render_template('dashboard.html')
