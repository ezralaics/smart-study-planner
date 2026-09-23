from flask import Blueprint

educator_bp = Blueprint('educator', __name__, url_prefix='/educator')

from blueprints.educator import routes  # noqa: E402, F401
