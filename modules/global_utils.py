import json
from flask import current_app, request
from flask_socketio import emit
from modules import redis_client
from modules.models import Block
import pika


def hash_func(s):
    hash_val = 7
    s = s.strip()
    for i in range(32):
        hash_val = hash_val * 31 + ord(s[i])
    index = hash_val % 1000
    return index


def messageHandler(message_json, message=None):

    if message is not None:
        msg = message
    else:
        msg = json.loads(message_json)

    receiver = redis_client.get(msg['friendHashID'])

    if msg['type'] == 'nameChange' or msg['type'] == 'dpChange':
        check_for_block = None
    else:
        check_for_block = Block.query.filter_by(
            blockee_hashID=msg['userHashID'],
            blocker_hashID=msg['friendHashID']).first()

    if check_for_block is None:
        if receiver is None:
            pika_client = pika.BlockingConnection(
                pika.URLParameters(current_app.config['MQ_URL']))
            channel = pika_client.channel()
            queue_val = hash_func(msg['friendHashID'])
            channel.basic_publish(
                exchange='', routing_key=str(queue_val), body=message_json)
            channel.close()
        else:
            receiver = receiver.decode('utf-8')
            emit('message', message_json, room=receiver)
    try:
        emit('receipt', msg['id'], room=request.sid)
    except Exception:
        print("NameChange or DpChangeToFriends")
    return receiver
