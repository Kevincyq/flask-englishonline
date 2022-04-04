#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_mail import Message
from flaskr import mail
from flask import current_app as app
from flask import render_template


######定义发送邮件函数###############################
def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    #msg.body = text_body
    msg.html = html_body
    mail.send(msg)


#####发送密码重置邮件函数，send_mail函数调用Message()生成对应的邮件消息##########################
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[OBETalk] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.user_email],
               #text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token)
               )
