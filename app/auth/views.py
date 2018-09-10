from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import LoginForm, RegistrationForm, ForgotPasswordForm,\
    ChangePasswordForm, ChangeUsernameForm, ResetPasswordForm
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
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
            and request.endpoint \
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
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(current_app.config["MAIL_USERNAME"],
                "Gustibus - Reset Password",
                "mail/reset_password",
                user=user,
                token=token)
            flash('An email has been sent to that email address')
            return redirect(url_for('auth.forgot_password'))
    return render_template('auth/forgot_password.html', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('Password Updated')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid confirmation token for password reset - request another')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            flash('Password Updated!')
            return redirect(url_for('main.index'))
        else:
            form.old_password.data = ''
            form.password.data = ''
            form.password2.data = ''
            flash('Incorrect Current Password')
            return redirect(url_for('auth.change_password', form=form))
    return render_template('auth/change_password.html', form=form)

@auth.route('/change_username', methods=['GET', 'POST'])
@login_required
def change_username():
    form = ChangeUsernameForm()
    if form.validate_on_submit():
        current_user.username = form.new_username.data
        db.session.add(current_user)
        db.session.commit()
        flash('User name updated to ' + current_user.username)
        return redirect(url_for('main.index'))
    return render_template('auth/change_username.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
