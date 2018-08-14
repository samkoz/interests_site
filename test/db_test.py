from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///c:/Users/samko/Desktop/website/test/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    #email = db.Column(db.String(120), unique=True, nullable=False)
    #password = db.Column(db.String(20), unique=True, nullable=False
    join_time = db.Column(db.DateTime, nullable=False)
    entries = db.relationship('Entry', backref='user')

    def __repr__(self):
        return '<User {0}; Join time: {1}; Entries: {2}>'.format(self.username, self.join_time, self.entries)

class Entry(db.Model):
    __tablename__ = 'entries'
    id = db.Column(db.Integer, primary_key=True)
    entry = db.Column(db.Text, nullable=False)
    entry_time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return 'Entry: {0}; user: {1}'.format(self.entry, self.user.username)
