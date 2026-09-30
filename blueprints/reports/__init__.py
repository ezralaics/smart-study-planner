from flask import Blueprint

reports_bp = Blueprint('reports', __name__)

from blueprints.reports import routes
