import os
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from flaskr import db, login
import jwt
from time import time
from datetime import  datetime, timedelta
from flask import current_app as app
import base64

login.login_view = 'login'


class Role(db.Model):
    __tablename___ = 'role'
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(15))

    def __init__(self, id, name):
        self.role_id = id
        self.role_name = name

    def __repr__(self):
        return '{}'.format(self.role_name)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(40))
    password = db.Column(db.String(100))
    user_email = db.Column(db.String(50))
    phone = db.Column(db.String(11))
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'))
    register_at = db.Column(db.DateTime, index=True, default=datetime.now)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    role = db.relationship('Role', backref=db.backref('user', lazy='dynamic'))

    def __init__(self, username='test', email='test@example.com', phone='12345678901', identity='student'):
        self.username = username
        self.user_email = email
        self.phone = phone
        if identity == 'student':
            self.role_id = 1
        elif identity == 'teacher':
            self.role_id = 2


    def __repr__(self):
        return '{}'.format(self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'user_email': self.user_email,
            'role_id': self.role_id,
            'phone': self.phone,
            'register_at': self.register_at
        }
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'user_email', 'phone', 'role_id']:
            if field in data:
                setattr(self,field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.now()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)

        db.session.add(self)

        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.now() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.now():
            return None
        return user



    def get_reset_password_token(self, expires_in=1800):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    real_name = db.Column(db.String(40))
    gender = db.Column(db.String(10))
    grade = db.Column(db.Integer)
    phone = db.Column(db.String(11), unique=True)
    level = db.Column(db.String(24))
    region = db.Column(db.String(40))

    user = db.relationship('User', backref=db.backref('student', lazy='dynamic'))

    def __init__(self, student_id):
        self.student_id = student_id

    def __repr__(self):
        return '{}'.format(self.user)

    def get_student_profile(uid):
        pass

    def update_student_profile(self):
        pass


class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    real_name = db.Column(db.String(40))
    gender = db.Column(db.String(10))
    level = db.Column(db.Integer)

    user = db.relationship('User', backref=db.backref('teacher', lazy='dynamic'))

    def __init__(self, teacher_id):
        self.teacher_id = teacher_id

    def __repr__(self):
        return '{}'.format(self.user)


class Blog(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(400))
    created = db.Column(db.DateTime, index=True, default=datetime.now)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('blog', lazy='dynamic'))

    def __init__(self, title, body, author_id):
        self.title = title
        self.body = body
        self.author_id = author_id


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_type = db.Column(db.String(5))
    course_name = db.Column(db.String(20))
    course_day = db.Column(db.String(10))
    course_start_at = db.Column(db.Time)
    course_duration = db.Column(db.String(10))
    isBooked = db.Column(db.Boolean)

    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    teacher = db.relationship('User', backref=db.backref('course', lazy='dynamic'))

    def __init__(self, course_name, course_day, course_start_at, course_duration, teacher_id, course_type=10,
                 isBooked=0):
        self.course_type = course_type
        self.course_name = course_name
        self.course_day = course_day
        self.course_start_at = course_start_at
        self.course_duration = course_duration
        self.isBooked = isBooked
        self.teacher_id = teacher_id


class Session(db.Model):
    __tablename__ = 'cousession'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_date = db.Column(db.Date)
    created = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(10), default='Not Start')
    isPaid = db.Column(db.String(1), default='Y')
    cancel_sign = db.Column(db.Boolean, default=0)
    renew_sign = db.Column(db.Boolean, default=1)
    recurred_sign = db.Column(db.Boolean)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))

    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.teacher_id'))

    teacher = db.relationship('Teacher', backref=db.backref('session', lazy='dynamic'))
    student = db.relationship('Student', backref=db.backref('session', lazy='dynamic'))

    def __init__(self, session_date, course_id, student_id, teacher_id, recurred_sign):
        self.session_date = session_date
        self.course_id = course_id
        self.student_id = student_id
        self.teacher_id = teacher_id
        self.recurred_sign = recurred_sign

    def get_student_count(uid):
        count = Session.query.filter_by(student_id=uid, status='Finished').count()
        cancel_count = Session.query.filter_by(student_id=uid, status='Cancelled').count()
        not_start_count = Session.query.filter_by(student_id=uid, status='Not Start').count()
        return count, cancel_count, not_start_count

    def get_teacher_count(uid):
        count = Session.query.filter_by(teacher_id=uid, status='Finished').count()
        cancel_count = Session.query.filter_by(teacher_id=uid, status='Cancelled').count()
        not_start_count = Session.query.filter_by(teacher_id=uid, status='Not Start').count()
        return count, cancel_count, not_start_count

    def get_session(id):
        session = Session.query.filter_by(id=id).first()
        return session

    def stop_session(self):
        pass


class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))
    top_up_value = db.Column(db.Integer)
    price = db.Column(db.Integer)
    top_up_time = db.Column(db.DateTime, index=True, default=datetime.now)

    student = db.relationship('Student', backref=db.backref('payment', lazy='dynamic'))

    def __init__(self, student_id, value, price):
        self.student_id = student_id
        self.top_up_value = value
        self.price = price

    def get_payment_count(uid):
        last_payment = Payment.query.filter_by(student_id=uid).order_by(Payment.top_up_time.desc()).first()
        payment_times = Payment.query.filter_by(student_id=uid).count()
        payments = Payment.query.filter_by(student_id=uid).all()
        total_values = 0
        for payment in payments:
            total_values += payment.top_up_value
        return total_values, last_payment, payment_times

    def get_payment_detail(self):
        pass


class Expense(db.Model):
    __tablename__ = 'expense'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.teacher_id'))
    expense_value = db.Column(db.Integer)
    price = db.Column(db.Integer)
    expense_time = db.Column(db.DateTime, index=True, default=datetime.now)

    teacher = db.relationship('Teacher', backref=db.backref('expense', lazy='dynamic'))

    def __init__(self, teacher_id, value, price):
        self.teacher_id = teacher_id
        self.expense_value = value
        self.price = price

    def get_expense_count(uid):
        last_expense = Expense.query.filter_by(teacher_id=uid).order_by(Expense.expense_time.desc()).first()
        expense_times = Expense.query.filter_by(teacher_id=uid).count()
        expenses = Expense.query.filter_by(teacher_id=uid).all()
        total_values = 0
        for expense in expenses:
            total_values += expense.expense_value
        return total_values, last_expense, expense_times


class Points(db.Model):
    __tablename__ = 'points'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))
    point_event = db.Column(db.String(10))
    point_increment = db.Column(db.Integer)
    point_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    student = db.relationship('Student', backref=db.backref('points', lazy='dynamic'))

    def add_point(self, event):
        self.point_event = event
        if event == '上课':
            self.point_increment = 50
        if event == '登录':
            self.point_increment = 5

    def query_TotalPoint(uid):
        total_points = 0
        records = Points.query.filter_by(student_id=uid).all()
        for record in records:
            total_points += record.point_increment
        if total_points < 5000:
            tier = 'Bronze'
        elif 5000 <= total_points < 10000:
            tier = 'Silver'
        elif 10000 <= total_points < 15000:
            tier = 'Gold'
        else:
            tier = 'Diamond'
        return total_points, tier

    def redeem_point(self):
        pass


class Awarding(db.Model):
    __tablename__ = 'awards'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))
    award_increment = db.Column(db.Integer)
    award_referee = db.Column(db.String(40))
    award_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    student = db.relationship('Student', backref=db.backref('awarding', lazy='dynamic'))

    def __init__(self, student_id, award_increment, award_referee):
        self.student_id = student_id
        self.award_increment = award_increment
        self.award_referee = award_referee

    def query_TotalAwards(uid):
        total_awards = 0
        records = Awarding.query.filter_by(student_id=uid).all()
        for record in records:
            total_awards += record.award_increment

        return total_awards

    def get_awards_count(uid):
        last_award = Awarding.query.filter_by(student_id=uid).order_by(Awarding.award_time.desc()).first()
        awards_times = Awarding.query.filter_by(student_id=uid).count()

        return last_award, awards_times


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


def init_app(app):
    app.teardown_appcontext()
    app.cli.add_command()
