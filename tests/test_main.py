from modules import create_app, socketio
from modules.config import DevelopmentConfig
import unittest
import json


class MainTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(DevelopmentConfig())

    def test_connect(self):
        client = socketio.test_client(self.app)
        assert not client.is_connected()
        client = socketio.test_client(self.app, query_string='?api_key=ankit')
        assert client.is_connected()
        client.disconnect()


class DatabaseTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(DevelopmentConfig())
        self.new_user = {''}

    def addData(self):
        client = socketio.test_client(self.app, query_string='?api_key=ankit')
        client.emit('new_user')


if __name__ == '__main__':
    unittest.main()
