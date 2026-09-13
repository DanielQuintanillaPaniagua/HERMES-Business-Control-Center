from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('ia_hermes', __name__)


@bp.route('/ia-hermes')
@login_required
def index():
    return render_template('ia_hermes.html')