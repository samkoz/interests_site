from flask import render_template, session, redirect, url_for, current_app
from . import main
from .. import db
from ..models import User

@main.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)
