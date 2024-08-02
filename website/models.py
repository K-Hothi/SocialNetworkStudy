from . import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    studying = db.Column(db.String(150))
    is_visible = db.Column(db.Boolean, default=True)
    classes = db.relationship('Class')
    notes = db.relationship('Notes')
    tests = db.relationship('Tests')
    qcards = db.relationship('Qcards')
    questions = db.relationship('Question')  # Relationship to questions posted by the user
    answers = db.relationship('Answer')  # Relationship to answers posted by the user
    followinguser = db.relationship('FollowingUser', foreign_keys='FollowingUser.user_id', backref='follower')


class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(150), unique=True)
    description = db.Column(db.String(200))
    following_count = db.Column(db.Integer)
    notes = db.relationship('Notes')
    tests = db.relationship('Tests')
    qcards = db.relationship('Qcards')
    questions = db.relationship('Question')  # Relationship to questions posted in the class


class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fileName = db.Column(db.String(150))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    likesCountNotes = db.Column(db.Integer)
    likesnotes = db.relationship('likesNotes')


class Tests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fileName = db.Column(db.String(150))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    likesCountTests = db.Column(db.Integer)
    likestests = db.relationship('likesTests')


class Qcards(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fileName = db.Column(db.String(150))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    likesCountCards = db.Column(db.Integer)
    likescards = db.relationship('likesCards')


class Following(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))


class likesNotes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'))


class likesTests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'))


class likesCards(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    card_id = db.Column(db.Integer, db.ForeignKey('qcards.id'))


class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.String(150))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    body = db.Column(db.Integer, db.ForeignKey('user.id'))


class FollowingUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_id_followed = db.Column(db.Integer, db.ForeignKey('user.id'))


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    answers = db.relationship('Answer')  # Relationship to answers posted for the question


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
