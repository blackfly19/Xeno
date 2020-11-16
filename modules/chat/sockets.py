from modules import socketio,MQ_URL
from .utils import hash_func
from flask_socketio import emit
from modules import redis_client 
from flask import request
import json
import pika
import time

@socketio.on('message')
def handleMessage(message):
    msg = json.loads(message)
    print(message)
    print(redis_client.get(msg['friendHashID']))
    receiver=redis_client.get(msg['friendHashID'])
    if receiver is None:
        pika_client = pika.BlockingConnection(pika.ConnectionParameters(host=MQ_URL,heartbeat=5))
        channel = pika_client.channel()
        queue_val = hash_func(msg['friendHashID'])
        #channel.queue_declare(queue=str(queue_val))
        channel.basic_publish(exchange='',routing_key=str(queue_val),body=message)
        channel.close()
    else:
        receiver = receiver.decode('utf-8')
        emit('message',message,room=receiver)
    emit('receipt',msg['id'],room=request.sid)

@socketio.on('xenoMessage')
def xenoMessage(message):
    msg = json.loads(message)
    print(message)
    print(redis_client.get(msg['friendHashID']))
    receiver=redis_client.get(msg['friendHashID'])
    receiver = receiver.decode('utf-8')
    emit('xenoMessage',message,room=receiver)
    emit('xenoReceipt',msg['id'],room=request.sid)