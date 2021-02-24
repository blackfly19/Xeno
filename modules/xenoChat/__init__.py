from flask import Blueprint

xenoChat = Blueprint('xenoChat',__name__)

from . import sockets
