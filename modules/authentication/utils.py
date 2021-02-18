from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
import cloudinary
import cloudinary.uploader as Uploader
from PIL import Image
import os
import io
import base64

def hash_func(s):
    hash_val = 7
    s = s.strip()
    for i in range(32):
        hash_val = hash_val * 31 + ord(s[i])
    index = hash_val%1000
    return index

def get_confirm_token(hashID,expires_sec=1800):
    s = Serializer(os.environ.get('SECRET_KEY'),expires_sec)
    return s.dumps({'hash_id':hashID}).decode('utf-8')

def convert_base64_to_url(encoded_img,imageFileName):
    in_mem = io.BytesIO(base64.b64decode(encoded_img))
    img = Image.open(in_mem)
    img.save(in_mem,format='JPEG')
    in_mem.seek(0)

    cloudinary.config(cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
                        api_key=current_app.config['CLOUDINARY_API_KEY'],
                        api_secret=current_app.config['CLOUDINARY_API_SECRET'])
    image_details = Uploader.upload(in_mem,public_id=imageFileName)
    return image_details['url']