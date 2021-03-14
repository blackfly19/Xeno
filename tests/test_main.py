from modules import create_app, socketio
from modules.config import DevelopmentConfig
import unittest
import uuid


class MainTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(DevelopmentConfig())

    def test_connect(self):
        client = socketio.test_client(self.app)
        assert not client.is_connected()
        client = socketio.test_client(self.app, query_string='?api_key=ankit')
        assert client.is_connected()
        print(client.get_received())
        client.disconnect()

    def test_mapHashID(self):
        client = socketio.test_client(self.app, query_string='?api_key=ankit')
        hashID = uuid.uuid1()
        client.emit('mapHashID', hashID.hex)

    def test_onlineUsers(self):



if __name__ == '__main__':
    unittest.main()
