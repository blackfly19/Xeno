from itsdangerous import JSONWebSignatureSerializer as Serializer
import os


def get_confirm_token(hashID):
    s = Serializer(os.environ.get('SECRET_KEY'))
    return s.dumps({'hash_id': hashID}).decode('utf-8')
