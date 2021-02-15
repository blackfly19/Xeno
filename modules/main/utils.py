import json
from flask_socketio import emit

def hash_func(s):
    hash_val = 7
    s = s.strip()
    for i in range(32):
        hash_val = hash_val * 31 + ord(s[i])
    index = hash_val%1000
    return index

def emit_for_auth(sid):
    emit('authorize',1,room=sid)

def ack():
    print("Message emitted")
