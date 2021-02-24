from modules import socketio, redis_client
from modules.models import Block
from .utils import hash_func
from flask_socketio import emit
from flask import request, current_app
import json
import pika
import time


@socketio.on('message')
def handleMessage(message):
    msg = json.loads(message)
    print(message)
    print(redis_client.get(msg['friendHashID']))
    receiver = redis_client.get(msg['friendHashID'])

    check_for_block = Block.query.filter_by(
        hashId_blockee=msg['userHashID'], hashId_blocker=msg['friendHashID']).first()
    if check_for_block is None:
        if receiver is None:
            pika_client = pika.BlockingConnection(pika.URLParameters(current_app.config['MQ_URL']))
            channel = pika_client.channel()
            queue_val = hash_func(msg['friendHashID'])
            # channel.queue_declare(queue=str(queue_val))
            channel.basic_publish(exchange='', routing_key=str(queue_val), body=message)
            channel.close()
        else:
            receiver = receiver.decode('utf-8')
            emit('message', message, room=receiver)
    emit('receipt', msg['id'], room=request.sid)


@socketio.on('unsent')
def unsent(messages):
    msgs = json.loads(messages)
    for msg in msgs:
        json_msg = json.dumps(msg)
        if redis_client.exists(msg['friendHashID']):
            receiver = redis_client.get(msg['friendHashID']).decode('utf-8')
            emit('message', json_msg, room=receiver)
        else:
            pika_client = pika.BlockingConnection(pika.URLParameters(current_app.config['MQ_URL']))
            channel = pika_client.channel()
            queue_val = hash_func(msg['friendHashID'])
            # channel.queue_declare(queue=str(queue_val))
            channel.basic_publish(exchange='', routing_key=str(queue_val), body=json_msg)
            channel.close()
        emit('receipt', msg['id'], room=request.sid)
