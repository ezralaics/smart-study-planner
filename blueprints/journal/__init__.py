from flask import Blueprint

journal_bp = Blueprint('journal', __name__)

from blueprints.journal import routes
