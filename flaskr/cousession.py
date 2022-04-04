#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' Session module '

__author__ = 'Kevin Chen'


from flask import (
     Blueprint, flash, redirect, render_template, request, url_for, current_app
)

from .auth import login_required
from flaskr import db
from .models import Session, Course, Payment, Points
from .course import get_course
from flask_login import current_user
from datetime import datetime,date,timedelta

bp = Blueprint('cousession', __name__, url_prefix='/cousession')



@bp.route('/cousession', methods=('GET',))
@login_required
def query():
    uid = current_user.id
    set_status()

    if current_user.role_id == 1:
        page = request.args.get('page', 1, type=int)
        pagination = Session.query.filter_by(student_id=uid).order_by(-Session.id).paginate(page, current_app.config['SESSION_PER_PAGE'], error_out=False)
        sessions = pagination.items
        next_url = url_for('cousession.query', page=pagination.next_num) \
            if pagination.has_next else None
        prev_url = url_for('cousession.query', page=pagination.prev_num) \
            if pagination.has_prev else None

        count, cancel_count, not_start_count = Session.get_student_count(uid=uid)

    elif current_user.role_id == 2:
        page = request.args.get('page', 1, type=int)
        pagination = Session.query.filter_by(teacher_id=uid).order_by(-Session.id).paginate(page, current_app.config['SESSION_PER_PAGE'], error_out=False)
        sessions = pagination.items
        next_url = url_for('cousession.query', page=pagination.next_num) \
            if pagination.has_next else None
        prev_url = url_for('cousession.query', page=pagination.prev_num) \
            if pagination.has_prev else None

        count, cancel_count, not_start_count = Session.get_teacher_count(uid=uid)

    else:
        page = request.args.get('page', 1, type=int)
        pagination = Session.query.order_by(-Session.id).paginate(page, current_app.config['SESSION_PER_PAGE'], error_out=False)
        sessions = pagination.items
        next_url = url_for('cousession.query', page=pagination.next_num) \
            if pagination.has_next else None
        prev_url = url_for('cousession.query', page=pagination.prev_num) \
            if pagination.has_prev else None
        count = Session.query.filter_by(status='Finished').count()
        cancel_count = Session.query.filter_by(status='Cancelled').count()
        not_start_count = Session.query.filter_by(status='Not Start').count()

    return render_template('cousession/cousession.html', pagination=pagination, sessions=sessions, count=count, cancel_count=cancel_count, not_start_count=not_start_count, next_url=next_url, prev_url=prev_url)

##Convert timedelta into datetime
def convert_timedelta(duration):
    seconds = duration.total_seconds()
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return hours,minutes,seconds

def set_status():

    current_date = date.today()
    courses = Course.query.all()
    uid = current_user.id
    for course in courses:
        results = Session.query.filter_by(course_id=course.id).order_by(Session.session_date)
        for result in results:
            if result.session_date < current_date and result.renew_sign == 1 and result.recurred_sign == 1 and result == results[-1] and compare_payment(result.student_id):
                session_date = result.session_date + timedelta(7)
                new_result = Session(session_date, result.course_id, result.student_id, result.teacher_id, result.recurred_sign)
                db.session.add(new_result)
                db.session.commit()
            elif result.session_date == current_date and result.cancel_sign == 0:
                t = course.course_start_at
                d = result.session_date
                start_time = datetime.combine(d,t)
                current_time = datetime.now()
                if start_time <= current_time:
                    result.status = 'Ongoing'
                    db.session.commit()
                if (current_time - start_time) >= timedelta(0,3600):
                    result.status = 'Finished'
                    #Points.add_point(event='上课')
                    db.session.commit()
            else:
                continue


    db.session.commit()

def compare_payment(uid):
    finished_times = Session.get_student_count(uid=uid)
    total_payment = Payment.get_payment_count(uid=uid)
    if finished_times[0] < total_payment[0]:
        return True
    else:
        return False

@bp.route('/<int:id>/book', methods=('POST','GET'))
@login_required
def book(id):

    course = get_course(id)
    teacher_id = course.teacher_id

    if request.method == 'POST':
        student_id = current_user.id
        course_id = id
        session_date = request.form['session_date']
        if request.form.get('recurred') == 'on':
            recurred_sign = 1
        else:
            recurred_sign = 0
        error = None

        if current_user.role_id == 2:
            error = 'Teacher cannot book course.'

        if error is not None:
            flash(error)
        else:
            session = Session(session_date, course_id, student_id, teacher_id, recurred_sign)
            db.session.add(session)
            course.isBooked = 1

            db.session.commit()
            return redirect(url_for('cousession.query'))

    return render_template('cousession/book.html', course=course, user_id=current_user.id)



@bp.route('/cousession/<int:id>/cancel', methods=('GET',))
def cancel(id):
    session = Session.get_session(id)
    error = None

    if session.status == 'Not Start' or current_user.role_id == 0:
       session.status = 'Cancelled'
       session.cancel_sign = 1
       session.renew_sign = 1

       db.session.commit()

    else:
       error = 'Session cannot be cancelled now!'

    if error is not None:
        flash(error)
    return redirect(url_for('cousession.query'))

@bp.route('/cousession/<int:id>/stop', methods=('GET',))
def stop(id):
    if current_user.role_id == 0:
        session = Session.get_session(id)
        course = get_course(session.course_id)
        if session.status == 'Not Start':
            session.status = 'Stopped'
            session.renew_sign = 0
            session.recurred_sign = 0
            session.cancel_sign = 1
            course.isBooked = 0

            db.session.commit()
    else:
        pass

    return redirect(url_for('cousession.query'))