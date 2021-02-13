from flask_socketio import emit
from flask import current_app
from modules import socketio,redis_client
import pika
from .utils import hash_func
from modules.models import User
import json
import time

@socketio.on('dashBroadcast')
def broadcast(message):
    print(message)
    users = User.query.all()
    jsons = []
    for user in users:
        if user.hashID != "00000000000000000000000000000000":
            msg = {'id':int(time.time() * 1000),"userHashID":"00000000000000000000000000000000",
                "friendHashID":user.hashID,"content":message}
            json_msg = json.dumps(msg)
            jsons.append(json_msg)

    for i,user in enumerate(users):
        receiver=redis_client.get(user.hashID)
        if receiver is None:
            pika_client = pika.BlockingConnection(pika.URLParameters(current_app.config['MQ_URL']))
            channel = pika_client.channel()
            queue_val = hash_func(user.hashID)
            #channel.queue_declare(queue=str(queue_val))
            channel.basic_publish(exchange='',routing_key=str(queue_val),body=jsons[i])
            channel.close()
        else:
            receiver = receiver.decode('utf-8')
            emit('message',jsons[i],room=receiver)