from flask import Flask,current_app
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from modules.config import Config
from modules.celery_worker import make_celery
import time
#import redis
from flask_redis import FlaskRedis
import pika
import os

socketio = SocketIO()
db = SQLAlchemy()
mail = Mail()
ma = Marshmallow()
redis_client = FlaskRedis()
async_task = None
#REDIS_IP = os.environ.get('REDIS_IP')
#REDIS_URL = os.environ.get('REDIS_URL')
#MQ_URL = os.environ.get('CLOUDAMQP_URL')

def create_app(debug=False,config_class=Config):
    app = Flask(__name__)
    app.debug = debug

    app.config.from_object(Config)

    db.init_app(app)
    #with app.app_context():
        #db.create_all()
        #db.session.commit()
    #async_task.conf.update(app.config)
    mail.init_app(app)
    ma.init_app(app)
    socketio.init_app(app,cors_allowed_origins="*",message_queue=app.config['REDIS_URL'],async_mode='eventlet')
    redis_client.init_app(app,health_check_interval=30)
    async_task = make_celery(app)

    redis_client.set('match_queue_count',0)

    from modules.main import main
    from modules.authentication import authentication
    from modules.chat import chat
    from modules.xenoChat import xenoChat
    from modules.dashboard import dashboard
    from modules.block import block
    from modules.feedbackAndChanges import feedbackAndChanges

    app.register_blueprint(main)
    app.register_blueprint(authentication)
    app.register_blueprint(chat)
    app.register_blueprint(xenoChat)
    app.register_blueprint(dashboard)
    app.register_blueprint(block)
    app.register_blueprint(feedbackAndChanges)

    from modules.xenoChat.utils import SeemaTaparia
    SeemaTaparia.delay()

    return app
