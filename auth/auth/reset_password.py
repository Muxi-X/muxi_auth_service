# coding: utf-8 

import random
from flask import request, jsonify
from .. import db
from . import auth 
from ..models import User
from ..mail import send_mail


@auth.route('/password/get_captcha/', methods=['POST'])
def get_captcha():
    """
    获取邮箱验证码
    """
    username = request.get_json().get('username') 
    email = request.get_json().get('email')
    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({}), 404
    captcha = '%04d' % random.randrange(0, 9999)
    send_mail(email, '木犀内网验证码', 'mail/reset', username=username, captcha=captcha)
    user.reset_t = user.generate_reset_token(captcha)
    return jsonify({}), 200


@auth.route('/password/check_captcha/', methods=['POST'])
def check_captcha():
    """
    检查邮箱验证码
    """
    captcha = request.get_json().get('captcha')
    email = request.get_json().get('email')
    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({}), 404
    try:
        tid, tcaptcha = User.verify_reset_token(user.reset_t)
    except TypeError:
        return jsonify({}), 403
    if tid != user.id or int(tcaptcha) != int(captcha):
        return jsonify({}), 403
    return jsonify({}), 200


@auth.route('/password/reset/', methods=['POST'])
def reset():
    """
    重置密码
    """
    captcha = request.get_json().get('captcha')
    email = request.get_json().get('email')
    new_password = request.get_json().get('new_password')
    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({}), 404
    try:
        tid, tcaptcha = User.verify_reset_token(user.reset_t)
    except TypeError:
        return jsonify({}), 403
    if tid != user.id or int(tcaptcha) != int(captcha):
        return jsonify({}), 403

    user.password = new_password
    user.reset_t = None
    db.session.add(user)
    db.session.commit()

    return jsonify({}), 200