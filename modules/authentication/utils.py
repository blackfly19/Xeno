from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import os


def get_confirm_token(hashID, expires_sec=1800):
    s = Serializer(os.environ.get('SECRET_KEY'), expires_sec)
    return s.dumps({'hash_id': hashID}).decode('utf-8')
