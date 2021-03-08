import json
from flask import current_app
from flask_socketio import emit
from modules import redis_client
from modules.models import Block
import pika
import io
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
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
    sender = redis_client.get(msg['userHashID']).decode('utf-8')

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
            channel.close()
        else:
            receiver = receiver.decode('utf-8')
            emit(msg['type'], message_json, room=receiver)

        if msg['type'] == 'message':
            emit('receipt', msg['id'], room=sender)
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
    print(camera_pic[0])
    print(display_pic[0])

    verify_result = face_client.face.verify_face_to_face(
        display_pic[0].face_id, camera_pic[0].face_id)
    print(verify_result.is_identical, verify_result.confidence)
    return verify_result.is_identical


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

