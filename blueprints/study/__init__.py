from flask import Blueprint

study_bp = Blueprint('study', __name__, url_prefix='/study')

from blueprints.study import routes
