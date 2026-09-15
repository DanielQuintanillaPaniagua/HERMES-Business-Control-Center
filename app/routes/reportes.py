from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('reportes', __name__)


@bp.route('/reportes')
@login_required
def index():
    return render_template('reportes.html')
