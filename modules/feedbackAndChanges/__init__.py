from flask import Blueprint

feedbackAndChanges = Blueprint('feedbackAndChanges', __name__)

from . import sockets
