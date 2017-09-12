# coding: utf-8

"""
models.py

    数据库模型
"""

from . import db, login_manager
from itsdangerous import JSONWebSignatureSerializer as Serializer
from itsdangerous import TimedJSONWebSignatureSerializer as TJSSerializer 
from random import seed
from flask import current_app, request, url_for
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import AnonymousUserMixin
from datetime import datetime
import sys
import bleach
import markdown
import hashlib
import base64

class Permission:
    """
    用户权限定义(base 16)
    """
    COMMENT = 0x02  # 评论权限
    WRITE_ARTICLES = 0x04  # 写文章权限
    MODERATE_COMMENTS = 0x08  # 修改评论权限
    ADMINISTER = 0x80  # 管理员权限，修改所有

class Role(db.Model):
    """
    用户角色定义
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        """
        插入角色
            1.User: 可以评论、写文章 true(默认)
            2.Moderator: 可以评论写文章,删除评论
            3.Administer: 管理员(想干什么干什么)
        需调用此方法，创建角色
        """
        roles = {
            # | 表示按位或操作,base 16进行运算
            'User': (Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)  # 添加进数据库
        db.session.commit()  # 提交

    def __repr__(self):
        """该类的'官方'表示方法"""
        return '<Role %r>' % self.name

class User(db.Model, UserMixin):
    """用户类"""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True) # user id (auto generate)

    email = db.Column(db.String(164)) # email address
    birthday = db.Column(db.String(164)) # user's birthday
    hometown = db.Column(db.String(164)) # hometown address and coordinates
    group = db.Column(db.String(164)) # group info (be, fe, design, android, product)
    timejoin = db.Column(db.String(164)) # time of joining muxi
    timeleft = db.Column(db.String(164)) # time of leaving muxi
    username = db.Column(db.String(164), unique=True)
    password_hash = db.Column(db.String(164))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    left = db.Column(db.Boolean)
    reset_t = db.Column(db.String)

    info = db.Column(db.Text) # talk about yourself
    # url of your avatar (suggestion: upload to qiniu or imugur)
    # tool: Drag (https://github.com/bHps2016/Drag)
    avatar_url = db.Column(db.Text)

    # blog and social networks' urls
    personal_blog = db.Column(db.Text)
    github = db.Column(db.Text)
    flickr = db.Column(db.Text)
    weibo = db.Column(db.Text)
    zhihu = db.Column(db.Text)


    def __init__(self, **kwargs):
        """用户角色实现"""
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    def can(self, permissions):
        """判断用户权限"""
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_admin(self):
        """判断当前用户是否是管理员"""
        return self.role_id == 2

    @property
    def password(self):
        """将密码方法设为User类的属性"""
        raise AttributeError('密码原始值保密, 无法保存!')

    @password.setter
    def password(self, password):
        """设置密码散列值"""
        password = base64.b64decode(password)
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """验证密码散列值"""
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self):
        """generate a token"""
        s = Serializer(
            current_app.config['SECRET_KEY']
        )
        return s.dumps({'id': self.id})

    def generate_reset_token(self, captcha):
        s = TJSSerializer(current_app.config['SECRET_KEY'], expires_in=10*60)
        data = {
            'id': self.id,
            'captcha': captcha
        }
        return s.dumps(data)

    @staticmethod
    def verify_reset_token(token):
        s = TJSSerializer(current_app.config['SECRET_KEY'], expires_in=10*60)
        try:
            data = s.loads(token)
        except SignatureExpired, BadSignature:
            return False
        id = data.get('id') # id int
        captcha = data.get('captcha')
        return id, captcha

    @staticmethod
    def verify_auth_token(token):
        """verify the user with token"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        # get id
        return User.query.get_or_404(data['id'])

    def to_json(self):
        json_user = {
            'id' : self.id,
            'username' : self.username,
            'email' : self.email
        }

    @staticmethod
    def from_json(json_user):
        u = User(
            username = json_user.get('username'),
            password = json_user.get('password'),
            email = json_user.get('email')
        )
        return u

    def __repr__(self):
        return "%r :The instance of class User" % self.username


class AnonymousUser(AnonymousUserMixin):
    """
	匿名用户类
	谁叫你匿名，什么权限都没有
	"""

    def can(self, permissions):
        return False

    def is_admin(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    """flask-login要求实现的用户加载回调函数
		依据用户的unicode字符串的id加载用户"""
    return User.query.get(int(user_id))

