import json
from flask import current_app
from flask_socketio import emit
from sqlalchemy import exc
from modules import redis_client, db
from modules.models import Block, User
import pika
import io
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from exponent_server_sdk import DeviceNotRegisteredError, PushClient
from exponent_server_sdk import PushMessage, PushResponseError, PushServerError
from requests.exceptions import ConnectionError, HTTPError
import rollbar
import base64
import cloudinary
import cloudinary.uploader as Uploader
from PIL import Image


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

    if msg['type'] != 'message':
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
            if msg['type'] == 'message':
                user = User.query.filter_by(hashID=msg['userHashID']).first()
                friend = User.query.filter_by(hashID=msg['friendHashID']).first()
                token_id = friend.notif_token
                notifications(token_id, user.username, msg['content'])
            channel.close()
        else:
            receiver = receiver.decode('utf-8')
            emit(msg['type'], message_json, room=receiver)

    return receiver


def face_verify(image_url, encoded_img):
    KEY = '119eb67123d04e2b9240d563e8d3e241'
    ENDPOINT = 'https://xeno-faceapi.cognitiveservices.azure.com/'

    in_mem = io.BytesIO(base64.b64decode(encoded_img))

    face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))
    display_pic = face_client.face.detect_with_url(
        url=image_url, detection_model='detection_02')
    camera_pic = face_client.face.detect_with_stream(
        in_mem, detection_model='detection_02')

    verify_result = face_client.face.verify_face_to_face(
        display_pic[0].face_id, camera_pic[0].face_id)
    print(verify_result.is_identical, verify_result.confidence)
    if verify_result.confidence > 0.42:
        return True
    else:
        return False


def convert_base64_to_url(encoded_img, imageFileName):
    in_mem = io.BytesIO(base64.b64decode(encoded_img))
    img = Image.open(in_mem)
    img.save(in_mem, format='JPEG')
    in_mem.seek(0)

    cloudinary.config(cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
                      api_key=current_app.config['CLOUDINARY_API_KEY'],
                      api_secret=current_app.config['CLOUDINARY_API_SECRET'])
    image_details = Uploader.upload(
        in_mem, public_id=imageFileName, invalidate=True)
    return image_details['url']


def notifications(token, title, message, extra=None):
    try:
        response = PushClient().publish(PushMessage(to=token,
                                                    title=title,
                                                    priority='high',
                                                    sound='default',
                                                    body=message,
                                                    data=extra))
    except PushServerError as exc:
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': message,
                'extra': extra,
                'errors': exc.errors,
                'response_data': exc.response_data,
            })
        raise
    except (ConnectionError, HTTPError) as exc:
        rollbar.report_exc_info(
            extra_data={'token': token, 'message': message, 'extra': extra})
#        raise self.retry(exc=exc)

    try:
        response.validate_response()
    except DeviceNotRegisteredError:
        from notifications.models import PushToken
        PushToken.objects.filter(token=token).update(active=False)
    except PushResponseError as exc:
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': message,
                'extra': extra,
                'push_response': exc.push_response._asdict(),
            })
#        raise self.retry(exc=exc)


def transactionFail(original_function):
    def wrapperFunction(*args, **kwargs):
        try:
            return original_function(*args, **kwargs)
        except exc.SQLAlchemyError as e:
            print(e)
            db.session.rollback()
    return wrapperFunction
