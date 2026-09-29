from flask import Blueprint

life_bp = Blueprint('life', __name__)

from blueprints.life import routes
