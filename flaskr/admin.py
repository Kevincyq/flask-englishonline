#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' CMS module '

__author__ = 'Kevin Chen'

from flask import (
    Blueprint, redirect, render_template, url_for, request, current_app
)
from .models import User, Student, Teacher, Points, Payment, Awarding, Expense, Session
from flask_login import current_user
from .auth import login_required
from flaskr import admin

bp = Blueprint('admin', __name__, url_prefix='/admin')

class MyView(BaseView):

#这里类似于bp.route()，处理url请求

@expose('/admin')

def index(self):

return self.render('index.html')

admin.add_view(MyView(name=u'Hello'))
