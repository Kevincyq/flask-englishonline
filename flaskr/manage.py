#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' Profile module '

__author__ = 'Kevin Chen'


from flask import (
    Blueprint, redirect, render_template, url_for, request, current_app
)
from .models import User, Student, Teacher, Points, Payment, Awarding, Expense, Session
from flask_login import current_user
from .auth import login_required
from flaskr import db

bp = Blueprint('manage', __name__, url_prefix='/manage')

@bp.route('/query', methods=('GET',))
@login_required
def query():
    if current_user.role_id != 0:
        return redirect(url_for('index'))
    else:
        #user_id = current_user.id
        page = request.args.get('page', 1, type=int)
        pagination = User.query.order_by(User.id).paginate(page, current_app.config['SESSION_PER_PAGE'], error_out=False)
        users = pagination.items
        next_url = url_for('manage.query', page=pagination.next_num) \
            if pagination.has_next else None
        prev_url = url_for('manage.query', page=pagination.prev_num) \
            if pagination.has_prev else None
        count = User.query.count()
        return render_template('manage/manage_users.html', pagination=pagination, users=users, count=count, next_url=next_url, prev_url=prev_url)

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    user = User.query.filter_by(id=id).first()
    if user.role_id == 1:
        student = Student(user.id)
        if request.method == 'POST':
            pass
        return render_template('manage/manage_student_edit.html', student=student)
    else:
        teacher = Teacher(user.id)
        if request.method == 'POST':
            pass
        return render_template('manage/manage_teacher_edit.html', teacher=teacher)




@bp.route('/<int:id>/detail', methods=('GET',))
@login_required
def detail(id):
    user = User.query.filter_by(id=id).first()
    if user.role_id == 1:
        student = Student.query.filter_by(student_id=id).first()
        count = Session.get_student_count(student.student_id)
        points, tier = Points.query_TotalPoint(uid=id)
        payments = Payment.get_payment_count(uid=id)
        awards = Awarding.query_TotalAwards(uid=id)
        return render_template('/manage/manage_student_query.html', student=student, count=count, points=points, tier=tier, payments=payments, awards=awards)
    elif user.role_id == 2:
        teacher = Teacher.query.filter_by(teacher_id=id).first()
        expense = Expense.get_expense_count(uid=id)
        count = Session.get_teacher_count(teacher.teacher_id)
        return render_template('/manage/manage_teacher_query.html', teacher=teacher, level=teacher.level, count=count, expense=expense)
    else:
        return redirect(url_for('manage.query'))


@bp.route('/<int:id>/remove', methods=('GET', 'POST'))
@login_required
def remove(id):
    user = User.query.filter_by(id=id).first()
    if user.role_id != 0:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('manage.query'))


@bp.route('/awards', methods=('GET',))
@login_required
def awards():
    if current_user.role_id != 0:
        return redirect(url_for('index'))
    else:
        page = request.args.get('page', 1, type=int)
        pagination = Awarding.query.order_by(Awarding.id).paginate(page, current_app.config['SESSION_PER_PAGE'], error_out=False)
        awards = pagination.items
        next_url = url_for('manage.awards', page=pagination.next_num) \
            if pagination.has_next else None
        prev_url = url_for('manage.awards', page=pagination.prev_num) \
            if pagination.has_prev else None
        return render_template('manage/manage_awards.html', pagination=pagination, awards=awards, next_url=next_url, prev_url=prev_url)

@bp.route('/grant', methods=('GET', 'POST'))
@login_required
def grant():

    if request.method == 'POST':
        student_id = request.form['student_id']
        award_increment = request.form['award_increment']
        award_referee = request.form['award_referee']

        award = Awarding(student_id, award_increment, award_referee)
        db.session.add(award)
        db.session.commit()
        return redirect(url_for('manage.awards'))

    return render_template('/manage/grant.html')


@bp.route('/payment', methods=('GET',))
@login_required
def payment():
    if current_user.role_id != 0:
        return redirect(url_for('index'))
    else:
        page = request.args.get('page', 1, type=int)
        pagination = Payment.query.order_by(Payment.id).paginate(page, current_app.config['SESSION_PER_PAGE'], error_out=False)
        payments = pagination.items
        next_url = url_for('manage.payment', page=pagination.next_num) \
            if pagination.has_next else None
        prev_url = url_for('manage.payment', page=pagination.prev_num) \
            if pagination.has_prev else None
        return render_template('manage/manage_payment.html', pagination=pagination, payments=payments, next_url=next_url, prev_url=prev_url)


@bp.route('/top_up', methods=('GET', 'POST'))
@login_required
def top_up():

    if request.method == 'POST':
        student_id = request.form['student_id']
        top_up_value = request.form['top_up_value']
        price = request.form['price']
        payment = Payment(student_id, top_up_value, price)
        db.session.add(payment)
        db.session.commit()
        return redirect(url_for('manage.payment'))

    return render_template('/manage/top_up.html')

@bp.route('/expense', methods=('GET',))
@login_required
def expense():
    if current_user.role_id != 0:
        return redirect(url_for('index'))
    else:
        page = request.args.get('page', 1, type=int)
        pagination = Expense.query.order_by(Expense.id).paginate(page, current_app.config['SESSION_PER_PAGE'], error_out=False)
        expenses = pagination.items
        next_url = url_for('manage.expense', page=pagination.next_num) \
            if pagination.has_next else None
        prev_url = url_for('manage.expense', page=pagination.prev_num) \
            if pagination.has_prev else None

        return render_template('manage/manage_expense.html', pagination=pagination, expenses=expenses, next_url=next_url, prev_url=prev_url)

@bp.route('/pay', methods=('GET','POST'))
@login_required
def pay():
    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        expense_value = request.form['expense_value']
        price = request.form['price']
        expense = Expense(teacher_id, expense_value, price)
        db.session.add(expense)
        db.session.commit()
        return redirect(url_for('manage.expense'))
    return render_template('/manage/pay_tuition.html')



