#coding: utf-8
import unittest
from flask import current_app , url_for,jsonify
from auth import create_app
from flask_sqlalchemy import SQLAlchemy
import random
from auth.models import User
import json
TOKEN = str(0)
TOKEN2 = str(0)
TOKEN1 = str(0)
db = SQLAlchemy()
number = random.randint(900,2000)

class BasicTestCase(unittest.TestCase) :
    def setUp(self) :
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self) :
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exist(self) :
        self.assertFalse(current_app is None)

    def test_a_signup(self) :
        response = self.client.post(
                    url_for('auth.signup',_external=True),
                    data = json.dumps({
                        "username" : str(number) ,
                        "email" : str(number) ,
                        "password" : str(number) }) ,
                    content_type = 'application/json')
        self.assertTrue( response.status_code == 200 )

    def test_b_login(self) :
        response = self.client.post(
                    url_for('auth.login',_external=True),
                    data = json.dumps({
                        "password" : str(number) ,
                        "email" : str(number)
                        }) ,
                    content_type = 'application/json'
                    )
        s = json.loads(response.data)['token']
        global TOKEN
        TOKEN = s
        self.assertTrue( response.status_code == 200 )

    def test_z_get_profile(self) :
        response = self.client.get(
                    url_for('auth.show_profile',_external=True) ,
                    headers = {
                        "token" : TOKEN ,
                        "Content_Type" : "application/json"
                        } ,
                    content_type = 'application/json'
                    )
        self.assertTrue ( response.status_code == 200 )

    def test_z_edit_profile(self) :
        response = self.client.post(
                    url_for('auth.edit_profile',_external=True) ,
                    headers = {
                        "token" : TOKEN ,
                        "Accpet" : "application/json" ,
                        "Content_Type" : "application/json"
                        } ,
                    data = json.dumps({
                        "info" : "2333" ,
                        "avatar_url" : "1234" ,
                        "flickr" : "1" ,
                        "github" : "2" ,
                        "group" : "3" ,
                        "hometown" : "4" ,
                        "personal_blog" : "5" ,
                        "timejoin" : "6" ,
                        "timeleft" : "7" ,
                        "weibo" : "8" ,
                        "zhihu" : "9" ,
                        "birthday" : "10" ,
                        }) ,
                    content_type = 'application/json' ,
                    )
        self.assertTrue( response.status_code == 200 )


