from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from modules.config import Config
from celery import Celery
import threading
import eventlet
import time
import redis
import pika
import os

#redis-cli -h xeno.redis.cache.windows.net -p 6379 -a 6RQloG0iuUQxMDtvcsiK5JpaElI8poZIBIfHhSOH3LQ=


socketio = SocketIO()
db = SQLAlchemy()
mail = Mail()
ma = Marshmallow()
REDIS_IP = os.environ.get('REDIS_IP')
REDIS_URL = os.environ.get('REDIS_URL')
MQ_URL = os.environ.get('CLOUDAMQP_URL')

redis_client = redis.StrictRedis(host=REDIS_IP,port=6379)

def create_app(debug=False,config_class=Config):
    app = Flask(__name__)
    app.debug = debug

    eventlet.monkey_patch()

    app.config.from_object(Config)

    db.init_app(app)
    #with app.app_context():
        #db.create_all()
        #db.session.commit()
    #async_task.conf.update(app.config)
    mail.init_app(app)
    ma.init_app(app)
    socketio.init_app(app,cors_allowed_origins="*",message_queue=REDIS_URL,async_mode='eventlet')
    
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
