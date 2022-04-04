#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' Course module '

__author__ = 'Kevin Chen'


from flask import (
     Blueprint, flash, redirect, render_template, request, url_for, current_app
)
from flaskr import db
from .auth import login_required
from .models import Course, User


bp = Blueprint('course', __name__, url_prefix='/course')

@bp.route('/curriculum', methods=('GET',))
def query_curriculum():
    return render_template('curriculum.html')

@bp.route('/course', methods=('GET',))
@login_required
def query():
    page = request.args.get('page', 1, type=int)
    pagination = Course.query.paginate(page, current_app.config['COURSES_PER_PAGE'], error_out=False)
    courses = pagination.items
    next_url = url_for('course.query', page=pagination.next_num) \
        if pagination.has_next else None
    prev_url = url_for('course.query', page=pagination.prev_num) \
        if pagination.has_prev else None

    return render_template('course/course.html', pagination=pagination, courses=courses, next_url=next_url, prev_url=prev_url)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    teacher_list = User.query.filter_by(role_id='2').all()

    if request.method == 'POST':
        course_type = request.form['course_type']
        course_name = request.form['course_name']
        course_day = request.form['course_day']
        course_start_at = request.form['course_start_at']
        course_duration = request.form['course_duration']
        teacher = request.form['teacher']
        error = None

        if not course_name:
            error = 'Name is required.'
        if not course_type:
            error = 'Type is required.'
        if not course_day:
            error = 'Day is required.'
        if not course_start_at:
            error = 'Starting time is required.'
        if not course_duration:
            error = 'Duration is required.'
        if not teacher:
            error = 'Teacher is required.'

        if error is not None:
            flash(error)
        else:
            teacher_id = User.query.filter_by(username=teacher).first().id
            course = Course(course_name, course_day, course_start_at, course_duration, teacher_id)
            db.session.add(course)
            db.session.commit()
            return redirect(url_for('course.query'))

    return render_template('course/create.html', teacher_list=teacher_list)

def get_course(id):
    course = Course.query.filter_by(id=id).first()

    return course

@bp.route('/<int:id>/delete', methods=('POST','GET'))
@login_required
def delete(id):
    course = Course.query.filter_by(id=id).first()
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('course.query'))


