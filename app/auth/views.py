from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import LoginForm, RegistrationForm, ForgotForm
from ..models import User
from .. import db
from datetime import datetime
from ..email import send_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # need to put something in this criteria for 'and not user.temp_password'
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
        token = new_user.generate_confirmation_token()
        # this will need to be updated to the email above once real users are involved
        send_email(current_app.config["MAIL_USERNAME"],
            "Gustibus Registration",
            "mail/registration",
            user=new_user,
            token=token)
        flash('A confirmation email has been sent to your account.')
        return redirect(url_for('main.index'))
    return render_template('auth/registration.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation lknk is invalid or has expired.')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', user=current_user)

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_app.config["MAIL_USERNAME"],
        "Gustibus Registration",
        "mail/registration",
        user=current_user,
        token=token)
    flash('A new confirmation email has been sent to {}'.format(current_user.email))
    return redirect(url_for('main.index'))

@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    # this may run into the problem of people changing other people's passwords.
    # also, this right now does not force someone to update their temporary password
    # need to redirect to login and then check if temp password; if so, redirect to password reset
    form = ForgotForm()
    if form.validate_on_submit():
        email = form.email.data
        # this should also probably be randomly generated
        temp_password = 'abc123'
        forgotten_user = User.query.filter_by(email=email).first()
        forgotten_user.password = temp_password
        # need to update user.temp_password = True here
        send_email(email, "Gustibus - Forgotten Password", "mail/forgot",
            username=forgotten_user.username, temp_password=temp_password)
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot.html', form=form)
#
# @auth.route('/password_reset', methods=['GET', 'POST'])
# def password_reset():
#     form = PasswordResetForm()
#     # need to reset password
#     # need to set temp_password to None
#     pass

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
