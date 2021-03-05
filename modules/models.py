from modules import db


class User(db.Model):
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    hashID = db.Column('hashID', db.String(40), unique=True, nullable=False)
    imageUrl = db.Column('imageUrl', db.String(512))
    username = db.Column('username', db.String(60), nullable=False)
    email = db.Column('email', db.String(100), nullable=False, unique=True)
    phone = db.Column('phone', db.String(10), nullable=False, unique=True)
    notif_token = db.Column('notif_token', db.String(64),
                            nullable=False, unique=True)
    verified = db.Column('verified', db.Boolean, nullable=False)
    interest_1 = db.Column('interest1', db.String(150), nullable=True)
    interest_2 = db.Column('interest2', db.String(150), nullable=True)
    interest_3 = db.Column('interest3', db.String(150), nullable=True)
    interest_4 = db.Column('interest4', db.String(150), nullable=True)
    interest_5 = db.Column('interest5', db.String(150), nullable=True)
    block = db.relationship('Block', backref='user_details', lazy=True,
                            foreign_keys='Block.blocker_hashID')
    friends = db.relationship('FriendList', backref='user_details',
                              lazy=True, foreign_keys='FriendList.user_hashID')


class Block(db.Model):
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    blocker_hashID = db.Column(
        db.String(40), db.ForeignKey('user.hashID'), nullable=False)
    blockee_hashID = db.Column(
        db.String(40), db.ForeignKey('user.hashID'), nullable=False)


class FriendList(db.Model):
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user_hashID = db.Column(
        db.String(40), db.ForeignKey('user.hashID'), nullable=False)
    friend_hashID = db.Column(
        db.String(40), db.ForeignKey('user.hashID'), nullable=False)
