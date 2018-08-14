from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SubmitField
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import Required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'password'
# app.config['SQLALCHEMY_DATABASE_URI'] =\
#     'sqlite:///'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

# forms
class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

# routes
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
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




"""
Clients (web browsers) send requests to servers which directs them to flask appliclation
For each URL passed to the application, it uses routes to determine what code to run

Decorators: wrap functions, modifying their behavior (example - you perform routing
then you execute your  function)

Return values of decorated routing functions is what the client sees

Dynamic routing: '/user/<name>' is closed in angle brackets

HTTP protocol requires HTML and a status code returned (default 200 in Flask)
"""
