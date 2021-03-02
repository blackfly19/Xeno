from modules import create_app,socketio
from modules.config import DevelopmentConfig
import unittest

class XenoTest(unittest.TestCase):

    def __init__(self):
        self.app = create_app(DevelopmentConfig())

    def test_main():
        client = socketio.test_client(self.app)
        assert client.is_connected()

"""def socketio_test():

    app = create_app(DevelopmentConfig()) 
    flask_test_client = app.test_client()
    socketio_test_client = socketio.test_client(app,flask_test_client=flask_test_client)
    assert socketio_test_client.is_connected()"""

if __name__ == '__main__':
    unittest.main()