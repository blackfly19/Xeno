from modules import create_app,socketio
from modules.config import DevelopmentConfig

def socketio_test():

    app = create_app(DevelopmentConfig()) 
    flask_test_client = app.test_client()
    socketio_test_client = socketio.test_client(app,flask_test_client=flask_test_client)
    assert socketio_test_client.is_connected()

socketio_test()