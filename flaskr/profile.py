#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' Profile module '

__author__ = 'Kevin Chen'

from flask import (
    Blueprint, redirect, render_template, url_for, request, flash
)

from flaskr import db
from .models import User, Student, Teacher, Payment, Points, Awarding, Expense
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import ValidationError, DataRequired, EqualTo

from flask_login import current_user
import logging
logging.basicConfig(level=logging.INFO)

bp = Blueprint('profile', __name__, url_prefix='/profile')


# 根据profile URL带进来的id，判断用户角色，并重定向到对应视图处理函数
@bp.route('/redirection', methods=('GET',))
def redirection():
    id = current_user.id
    if current_user.role_id == 1:
        student = Student.query.filter_by(student_id=id).first()
        return render_template('profile/student.html', student=student)
    if current_user.role_id == 2:
        teacher = Teacher.query.filter_by(teacher_id=id).first()
        return render_template('profile/teacher.html', teacher=teacher)
    if current_user.role_id == 0:
        return redirect(url_for('manage.query'))


@bp.route('/edit', methods=('GET', 'POST'))
def edit():
    id = current_user.id
    if current_user.role_id == 1:
        student = Student.query.filter_by(student_id=id).first()
        if request.method == 'POST':
            real_name = request.form['real_name']
            gender = request.form['gender']
            grade = request.form['grade']
            phone = request.form['phone']
            region = request.form['region']

            error = None

            if not checkPhone(phone):
                error = 'Invalid Phone number!'
                logging.info('the error is %s' %error)

            if error is not None:
                flash(error)
            else:
                student.real_name = real_name
                student.gender = gender
                student.grade = grade
                student.phone = phone
                student.region = region
                db.session.commit()
                return redirect(url_for('profile.redirection'))

        return render_template('profile/edit_stu.html', student=student)

    if current_user.role_id == 2:
        teacher = Teacher.query.filter_by(teacher_id=id).first()
        if request.method == 'POST':
            real_name = request.form['real_name']
            gender = request.form['gender']

            error = None

            if error is not None:
                flash(error)
            else:
                teacher.real_name = real_name
                teacher.gender = gender
                db.session.commit()
                return redirect(url_for('profile.redirection'))
        return render_template('profile/edit_tea.html', teacher=teacher)


@bp.route('/change_password', methods=('GET', 'POST'))
def change_password():
    form = ChangePasswordForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).first()
        user.set_password(form.passwordNew.data)
        db.session.commit()
        return redirect(url_for('profile.redirection'))
    return render_template('/profile/change_password.html', form=form)

@bp.route('/update_password', methods=('GET', 'POST'))
def update_password():
    form = ChangePasswordForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).first()
        user.set_password(form.passwordNew.data)
        db.session.commit()
        return redirect(url_for('profile.redirection'))
    return render_template('/profile/update_password.html', form=form)

@bp.route('/check_payment', methods=('GET',))
def check_payment():
    uid = current_user.id
    total_values, last_payment, payment_times = Payment.get_payment_count(uid=uid)
    return render_template('/profile/check_payment.html', total_values=total_values, last_payment=last_payment, payment_times=payment_times)


@bp.route('/check_points', methods=('GET',))
def check_points():
    uid = current_user.id
    total_points, tier = Points.query_TotalPoint(uid=uid)

    return render_template('/profile/check_points.html', total_points=total_points, tier=tier)

@bp.route('/check_awards', methods=('GET',))
def check_awards():
    uid = current_user.id
    awards = Awarding.query_TotalAwards(uid=uid)
    last_award, awards_count = Awarding.get_awards_count(uid=uid)

    return render_template('/profile/check_awards.html', awards=awards, last_award=last_award, awards_count=awards_count)

@bp.route('/check_blog', methods=('GET',))
def check_blog():
    pass

@bp.route('/check_tuition', methods=('GET',))
def check_tuition():
    uid = current_user.id
    total_values, last_expense, expense_times = Expense.get_expense_count(uid=uid)
    return render_template('/profile/check_tuition.html', total_values=total_values, last_expense=last_expense, expense_times=expense_times)


def checkPhone(ph):
    if len(ph) != 11:
        return False
    elif ph[0] != '1':
        return False
    else:
        for i in range(1, 11):
            if ph[i] < '0' or ph[i] > '9':
                return False
        return True

class ChangePasswordForm(FlaskForm):
    passwordOld = PasswordField('Old Password', validators=[DataRequired()])
    passwordNew = PasswordField('New Password', validators=[DataRequired()])
    passwordNewRepeat = PasswordField('Password Again', validators=[DataRequired(), EqualTo('passwordNew')])
    submit = SubmitField('Change')

    def validate_password(self, passwordOld):
        user = User.query.filter_by(id=current_user.id).first()
        result = user.check_password(passwordOld.data)
        logging.info('existing password is %s' %passwordOld.data)
        if not result:
            raise ValidationError('Please enter the correct password!')
