# coding: utf-8

"""
    login.py
    ~~~~~~~~

    木犀官网登陆API

"""

from flask import jsonify, request
from . import auth
from ..models import User
from .. import db

@auth.route('/login/', methods=['POST'])
def login():
    username = request.get_json().get("username")
    pwd = request.get_json().get("password")

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({}), 403
    if not user.verify_password(pwd):
        return jsonify({}), 400

    token = user.generate_auth_token()
    return jsonify ({
        'token': token,
        }), 200

