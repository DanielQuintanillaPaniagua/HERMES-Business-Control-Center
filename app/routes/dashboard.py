from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@login_required
def index():
    """PÃ¡gina principal de HERMES tras iniciar sesiÃ³n."""
    return render_template('dashboard.html')
