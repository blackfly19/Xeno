import eventlet
eventlet.monkey_patch()

from modules import create_app,socketio
from modules.config import ProductionConfig,DevelopmentConfig
import os

configClass = None

if os.environ.get('FLASK_ENV') == 'production':
    configClass = ProductionConfig()
else:
    print("Server is in development environment")
    configClass = DevelopmentConfig()

app = create_app(configClass)

if __name__ == '__main__':
    socketio.run(app)
