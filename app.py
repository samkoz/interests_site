from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import Form
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from wtforms import StringField, SubmitField
from flask_mail import Mail, Message
import os
from wtforms.validators import Required

app = Flask(__name__)

app.config['SECRET_KEY'] = 'password'

# Database configurations
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///c:/Users/samko/Desktop/website/dev.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# Mail configurations
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
mail = Mail(app)

# emails
def send_email(to, subject, template, **kwargs):
    """
    # Testing w/in Flask shell
    flask shell
    from app import send_email
    send_email(app.config["MAIL_USERNAME"], "test", "mail/test")
    """
    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)

# forms
class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

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

# routes
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data, join_time=datetime.utcnow())
            db.session.add(user)
        session['name'] = form.name.data
        print(session['name'])
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html',
                                form=form,
                                name=session.get('name'),
                                current_time=datetime.utcnow())

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
