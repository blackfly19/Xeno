from modules import socketio, redis_client
from modules.global_utils import messageHandler
from flask_socketio import emit
from flask import request
import json


@socketio.on('message')
def handleMessage(message_json):
    message = json.loads(message_json)
    messageHandler(message_json=message_json, message=message)
    emit('receipt', message['id'], room=request.sid)


@socketio.on('unsent')
def unsent(messages):
    messages = json.loads(messages)
    sender = request.sid
    for message in messages:
        message_json = json.dumps(message)
        messageHandler(message_json=message_json, message=message)
        emit('receipt', message['id'], room=sender)


@socketio.on('friendTyping')
def typingIndicator(typing_data):
    typing = json.loads(typing_data)
    receiver = redis_client.get(typing['friendHashID'])
    if receiver is not None:
        receiver = receiver.decode('utf-8')
        emit('friendTyping', typing_data, room=receiver)


@socketio.on_error()
def error_handler(e):
    print(e)
