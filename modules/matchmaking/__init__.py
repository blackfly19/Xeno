from flask import Blueprint

matchmaking = Blueprint('matchmaking',__name__)

from . import sockets