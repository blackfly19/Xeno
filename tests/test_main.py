from modules import create_app,socketio
from modules.config import DevelopmentConfig
import unittest

class XenoTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(DevelopmentConfig())

    def test_main(self):
        client = socketio.test_client(self.app)
        assert not client.is_connected()
        client = socketio.test_client(self.app,query_string='?api_key=ankit')
        assert client.is_connected()
        client.disconnect()

if __name__ == '__main__':
    unittest.main()