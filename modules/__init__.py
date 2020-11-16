from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from modules.config import Config
import redis
import pika
import os

socketio = SocketIO()
db = SQLAlchemy()
mail = Mail()
ma = Marshmallow()
REDIS_URL = os.environ.get('REDIS_URL')
MQ_URL = os.environ.get('CLOUDAMQP_URL')
redis_client = redis.Redis(REDIS_URL,db=0)
pika_client = pika.BlockingConnection(pika.ConnectionParameters(host=MQ_URL,heartbeat=5))

def create_app(debug=False,config_class=Config):
    app = Flask(__name__)
    app.debug = debug
    app.config.from_object(Config)

    db.init_app(app)
    #with app.app_context():
        #db.create_all()
        #db.session.commit()
    mail.init_app(app)
    ma.init_app(app)
    socketio.init_app(app,cors_allowed_origins="*")
    redis_client.set('match_queue_count',0)

    from modules.main import main
    from modules.authentication import authentication
    from modules.chat import chat
    from modules.matchmaking import matchmaking

    app.register_blueprint(main)
    app.register_blueprint(authentication)
    app.register_blueprint(chat)
    app.register_blueprint(matchmaking)

    return app