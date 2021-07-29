from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('test', __name__, url_prefix='/test')


@bp.route("/hey")
def hey():
    text_var = 'hey'
    return render_template('test/test.html', text_var=text_var)