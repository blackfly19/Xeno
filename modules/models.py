from modules import db,ma
from datetime import datetime as dt


class User(db.Model):
    id = db.Column('id',db.Integer,primary_key=True,autoincrement=True)
    hashID = db.Column('hashID',db.String(40),unique=True,nullable=False)
    imageUrl = db.Column('imageUrl',db.String(512))
    username = db.Column('username',db.String(60),nullable=False)
    email = db.Column('email',db.String(100),nullable=False,unique=True)
    phone = db.Column('phone',db.String(10),nullable=False,unique=True)
    notif_token = db.Column('notif_token',db.String(64),nullable=False,unique=True)
    verified = db.Column('verified',db.Boolean,nullable=False)

class UserSchema(ma.Schema):
    class Meta:
        fields = ['username','hashID','imageUrl']


