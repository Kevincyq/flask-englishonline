#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' Download module '

__author__ = 'Kevin Chen'

from flask import (
     Blueprint, render_template
)

bp = Blueprint('download', __name__, url_prefix='/download')

@bp.route('/', methods=('GET',))
def query():
    return render_template('download.html')
