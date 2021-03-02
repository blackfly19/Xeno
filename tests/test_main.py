from modules import create_app,socketio
from modules.config import DevelopmentConfig
import unittest

class XenoTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(DevelopmentConfig())

    def test_main(self):
        client = socketio.test_client(self.app)
        assert client.is_connected()

if __name__ == '__main__':
    unittest.main()