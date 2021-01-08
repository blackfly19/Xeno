from flask import Flask,current_app
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from modules.config import Config
from celery import Celery
import threading
import time
import redis
import pika
import os

socketio = SocketIO()
db = SQLAlchemy()
mail = Mail()
ma = Marshmallow()
REDIS_URL = 'redis://:6RQloG0iuUQxMDtvcsiK5JpaElI8poZIBIfHhSOH3LQ=@xeno.redis.cache.windows.net:6379/0'

MQ_URL = os.environ.get('CLOUDAMQP_URL')

redis_client = redis.StrictRedis(host='xeno.redis.cache.windows.net',password='6RQloG0iuUQxMDtvcsiK5JpaElI8poZIBIfHhSOH3LQ=',port=6379)

async_task = Celery(current_app.import_name,broker=REDIS_URL)

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
    socketio.init_app(app,cors_allowed_origins="*",message_queue=REDIS_URL)
    redis_client.set('match_queue_count',0)

    from modules.main import main
    from modules.authentication import authentication
    from modules.chat import chat
    from modules.matchmaking import matchmaking
    from modules.dashboard import dashboard

    app.register_blueprint(main)
    app.register_blueprint(authentication)
    app.register_blueprint(chat)
    app.register_blueprint(matchmaking)
    app.register_blueprint(dashboard)

    return app