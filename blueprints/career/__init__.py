from flask import Blueprint

career_bp = Blueprint('career', __name__)

from blueprints.career import routes
