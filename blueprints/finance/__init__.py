from flask import Blueprint

finance_bp = Blueprint('finance', __name__)

from blueprints.finance import routes
