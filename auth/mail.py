# coding: utf-8

from flask import render_template, jsonify
from flask_mail import Message, Mail
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
import time
from celery import Celery
from . import  app, celery, mails

#mails = Mail(app)
#celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'],backend=app.config['CELERY_RESULT_BACKEND'])

def msg_dict(to, subject, template, **kwargs):
    """
    生成邮件
    """
    msg = Message(
        subject=app.config['AUTH_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[to]
    )
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    return msg.__dict__

def send_mail(to, subject, template, **kwargs):
    """
    发送邮件
    """
    send_async_email.delay(msg_dict(to, subject, template, **kwargs))

@celery.task(default_retry_delay=30)
def send_async_email(msg_dict):
    with app.app_context():
        """
        异步方法
        """
        msg = Message()
        msg.__dict__.update(msg_dict)
        mails.send(msg)
