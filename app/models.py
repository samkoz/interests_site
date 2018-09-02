from . import db

# Association Tables
tag_entry_associations = db.Table('tag_entry_associations',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
    db.Column('entry_id', db.Integer, db.ForeignKey('entries.id'))
)

# db tables
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    #email = db.Column(db.String(120), unique=True, nullable=False)
    #password = db.Column(db.String(20), unique=True, nullable=False
    join_time = db.Column(db.DateTime, nullable=False)
    entries = db.relationship('Entry', backref='user', lazy='dynamic')

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

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(30), nullable=False)
    entries = db.relationship('Entry',
                                secondary=tag_entry_associations,
                                backref=db.backref('tags', lazy='dynamic'),
                                lazy='dynamic')

    def __repr__(self):
        return 'Tag: {0}'.format(self.tag)
