#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' Guide module '

__author__ = 'Kevin Chen'

from flask import (
     Blueprint, render_template
)

bp = Blueprint('guide', __name__, url_prefix='/guide')

@bp.route('/', methods=('GET',))
def query():
    return render_template('guide.html')

