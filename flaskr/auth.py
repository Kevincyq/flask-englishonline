import functools
import logging
logging.basicConfig(level=logging.INFO)
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flaskr import db
from flask_login import login_user, logout_user, current_user
from .models import User, Student, Teacher
from datetime import datetime
from .email import send_password_reset_email

from flask_babel import gettext as _

# Blueprint 是一种组织一组相关视图及其他代码的方式。创建了一个名称为 'auth' 的 Blueprint, Blueprint需要知道是在哪里定义的，
# 因此把 __name__ 作为函数的第二个参数。auth Blueprint包括register、login和logout视图
# url_prefix 会添加到所有与该Blueprint关联的 URL 前面
bp = Blueprint('auth', __name__, url_prefix='/auth')


# register视图
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    rtitle = _("Register")
    if request.method == 'POST' and form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, identity=form.identity.data, phone=form.phone.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        if user.role_id == 1:
            student = Student(user.id)
            db.session.add(student)
        if user.role_id == 2:
            teacher = Teacher(user.id)
            db.session.add(teacher)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', rtitle=rtitle, form=form)


# login视图
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    ltitle = _("Log in")
    if request.method == 'POST':
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)

        return redirect(url_for('index'))

    return render_template('auth/login.html', ltitle=ltitle, form=form)


@bp.before_app_request
def load_logged_in_user():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()

        db.session.commit()


# logout视图
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if current_user.is_authenticated is False:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/reset_password_request', methods=('GET', 'POST'))
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(user_email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=('GET', 'POST'))
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)

    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit() and request.method == 'POST':
        #logging.info('USER IS %s' %user)
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)



class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    phone = StringField('Phone', validators=[DataRequired()])
    identity = StringField('Identity', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('User is already registered.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')
