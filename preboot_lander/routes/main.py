from datetime import datetime
from flask import (
    Blueprint,
    render_template,
)

bp_main = Blueprint('main', __name__)


@bp_main.route('/', methods=['GET'])
@bp_main.route('/home', methods=['GET'])
def index():
    return render_template(
        'index.jinja',
        now=datetime.now()
    )
