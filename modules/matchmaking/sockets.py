from modules import socketio,redis_client
from modules.models import User
from flask_socketio import emit
import json
import time

@socketio.on('matchQueue')
def match(Hash):

    redis_client.rpush('matchqueue',Hash)
    redis_client.incr('match_queue_count')

    time.sleep(3)

    while int(redis_client.get('match_queue_count').decode('utf-8')) > 1:

        hash_user1 = redis_client.lpop('matchqueue')
        while redis_client.exists(hash_user1) != True or redis_client.hexists('cancel',hash_user1) == True:
            if redis_client.hexists('cancel',hash_user1) == True:
                redis_client.hdel('cancel',hash_user1)
            redis_client.decr('match_queue_count')
            if redis_client.exists('matchqueue') == False:
                break
            hash_user1 = redis_client.lpop('matchqueue')
        redis_client.decr('match_queue_count')
            
        if redis_client.exists('matchqueue') == False:
            print('Is None')
            redis_client.rpush('matchqueue',hash_user1)
            break

        hash_user2 = redis_client.lpop('matchqueue')
        while redis_client.exists(hash_user2) != True or redis_client.hexists('cancel',hash_user2) == True:
            if redis_client.hexists('cancel',hash_user2) == True:
                redis_client.hdel('cancel',hash_user2)
            redis_client.decr('match_queue_count')
            if redis_client.exists('matchqueue') == False:
                redis_client.rpush('matchqueue',hash_user1)
                redis_client.incr('match_queue_count')
                hash_user2 = None
                break
            hash_user2 = redis_client.lpop('matchqueue')
        redis_client.decr('match_queue_count')

        if hash_user2 is None:
            break
        
        print(hash_user1)
        print(hash_user2)

        hash_user1 = hash_user1.decode('utf-8')
        hash_user2 = hash_user2.decode('utf-8')

        #redis_client.decrby('match_queue_count',2)

        user1 = User.query.filter_by(hashID=hash_user1).first()
        user2 = User.query.filter_by(hashID=hash_user2).first()

        user1_json = json.dumps({'name':user1.username,'hashID':hash_user1,'imageUrl':user1.imageUrl})
        user2_json = json.dumps({'name':user2.username,'hashID':hash_user2,'imageUrl':user2.imageUrl})
        
        #json - dp url,name, hashid,interest list
        emit('xenoHashID',user1_json,room=redis_client.get(hash_user2).decode('utf-8'))
        emit('xenoHashID',user2_json,room=redis_client.get(hash_user1).decode('utf-8'))

@socketio.on('matchCancel')
def cancel(Hash):
    redis_client.hset('cancel',Hash,1)
