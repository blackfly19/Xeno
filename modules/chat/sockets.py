from modules import socketio, redis_client
from .utils import messageHandler
from flask_socketio import emit
import json


@socketio.on('message')
def handleMessage(message):
    messageHandler(message_json=message)


@socketio.on('unsent')
def unsent(messages):
    messages = json.loads(messages)
    for message in messages:
        message_json = json.dumps(message)
        messageHandler(message_json=message_json, message=message)


@socketio.on('friendTyping')
def typingIndicator(typing_data):
    typing = json.loads(typing_data)
    receiver = redis_client.get(typing['friendHashID']).decode('utf-8')
    emit('friendTyping', typing_data, room=receiver)
