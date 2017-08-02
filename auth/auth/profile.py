# coding: utf-8

"""
    profile.py
    ~~~~~~~~~~
    木犀官网资料API
"""

from flask import jsonify, request , g
from . import auth
from .decorators import login_required
from ..models import User
from .. import db
import datetime

@auth.route('/show_profile/<int:id>/', methods=['GET'])
@login_required
def show_profile(id):
    """读取用户信息"""
    ID = id
    user = User.query.filter_by(id=ID).first()

    return jsonify({
        "id": user.id,
        "email": user.email,
        "birthday": user.birthday,
        "hometown": user.hometown,
        "group": user.group,
        "timejoin": user.timejoin,
        "timeleft": user.timeleft,
        "username": user.username ,
        "info": user.info,
        "avatar_url": user.avatar_url,
        "personal_blog": user.personal_blog,
        "github": user.github,
        "flickr": user.flickr,
        "weibo": user.weibo,
        "zhihu": user.zhihu,
        }), 200


@auth.route('/edit_profile/', methods=['POST'])
@login_required
def edit_profile():
    """编辑用户信息"""
    ID = g.current_user.id
    user = User.query.filter_by(id=ID).first()

    user.avatar_url = request.get_json().get("avatar_url")
    user.birthday = request.get_json().get("birthday")
    user.flickr = request.get_json().get("flickr")
    user.github = request.get_json().get("github")
    user.group = request.get_json().get("group")
    user.hometown = request.get_json().get("hometown")
    user.info = request.get_json().get("info")
    user.personal_blog = request.get_json().get("personal_blog")
    user.timejoin = request.get_json().get("timejoin")
    user.timeleft = request.get_json().get("timeleft")
    user.weibo = request.get_json().get("weibo")
    user.zhihu = request.get_json().get("zhihu")

    db.session.add(user)
    db.session.commit()

    return jsonify({
            'changed' : ID ,
        }) , 200
