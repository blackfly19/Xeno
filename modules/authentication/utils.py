from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import os

def hash_func(s):
    hash_val = 7
    s = s.strip()
    for i in range(32):
        hash_val = hash_val * 31 + ord(s[i])
    index = hash_val%1000
    return index

def get_confirm_token(self,hashID,expires_sec=1800):
        s = Serializer(os.environ.get('SECRET_KEY'),expires_sec)
        return s.dumps({'hash_id':hashID}).decode('utf-8')