from flask import Flask
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

#redis-cli -h xeno.redis.cache.windows.net -p 6379 -a 6RQloG0iuUQxMDtvcsiK5JpaElI8poZIBIfHhSOH3LQ=


socketio = SocketIO()
db = SQLAlchemy()
mail = Mail()
ma = Marshmallow()
REDIS_URL = 'redis://:6RQloG0iuUQxMDtvcsiK5JpaElI8poZIBIfHhSOH3LQ=@xeno.redis.cache.windows.net:6379/0'
async_task = Celery(__name__,broker=Config.CELERY_BROKER_URL)
MQ_URL = os.environ.get('CLOUDAMQP_URL')

from modules.matchmaking.utils import SeemaTaparia,Limiter

redis_client = redis.StrictRedis(host='xeno.redis.cache.windows.net',password='6RQloG0iuUQxMDtvcsiK5JpaElI8poZIBIfHhSOH3LQ=',port=6379)
redis_client.delete('unacked')
redis_client.delete('unacked_index')
redis_client.delete('_kombu.binding.celery.pidbox')
redis_client.delete('_kombu.binding.celery')
redis_client.delete('_kombu.binding.celeryev')
redis_client.delete('celery')

def create_app(debug=False,config_class=Config):
    app = Flask(__name__)
    app.debug = debug
    app.config.from_object(Config)

    db.init_app(app)
    #with app.app_context():
        #db.create_all()
        #db.session.commit()
    async_task.conf.update(app.config)
    mail.init_app(app)
    ma.init_app(app)
    socketio.init_app(app,cors_allowed_origins="*",message_queue=REDIS_URL)
    redis_client.set('match_queue_count',0)

    SeemaTaparia.delay()
    Limiter.delay()


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
