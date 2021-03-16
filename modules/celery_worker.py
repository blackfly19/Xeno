from modules import create_app
from celery import Celery
from modules.config import ProductionConfig, DevelopmentConfig
import os


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery_app = None
if os.environ.get('FLASK_ENV') == 'production':
    celery_app = create_app(ProductionConfig())
else:
    celery_app = create_app(DevelopmentConfig())
    print("Celery in development config")

async_task = make_celery(celery_app)

from modules.xenoChat.utils import SeemaTaparia, keep_server_alive, notify

SeemaTaparia.delay(celery_app.config['SOCKETIO_URL'])
keep_server_alive.delay()
notify.delay()
# onlineUsers.delay(celery_app.config['SOCKETIO_URL'])
