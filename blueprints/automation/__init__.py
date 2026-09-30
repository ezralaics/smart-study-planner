from flask import Blueprint

automation_bp = Blueprint('automation', __name__)

from blueprints.automation import routes
