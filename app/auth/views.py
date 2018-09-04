from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
from . import auth
from .forms import LoginForm, RegistrationForm
from ..models import User
from .. import db
from datetime import datetime

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next=url_for('main.index')
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        join_time = datetime.utcnow()
        new_user = User(username=username, email=email, password=password, join_time=join_time)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, False)
        next = request.args.get('next')
        if next is None or not next.startswith('/'):
            next = url_for('main.index')
        return redirect(next)
    return render_template('auth/registration.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
