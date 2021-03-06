# hash function to get unique keys
import json
from flask import current_app, request
from flask_socketio import emit
from modules import redis_client
from modules.models import Block
import pika
from modules.global_utils import hash_func


def messageHandler(message_json, message=None):

    if message is not None:
        msg = message
    else:
        msg = json.loads(message_json)

    receiver = redis_client.get(msg['friendHashID'])

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
    emit('receipt', msg['id'], room=request.sid)
