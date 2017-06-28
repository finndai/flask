#-*-coding:utf-8-*-
import re
import unittest
from flask import url_for
from app import create_app,db
from app.models import User,Role

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):                     #'setup'小写U会报错
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True) #self.client为客户端测试对象，use_cookies启用则能接收和发送请求

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))   #get方法可以得到一个FlaskResponse对象，内容为调用视图函数得到的响应
        self.assertTrue('Stranger' in response.get_data(as_text=True))

    def test_register_and_login(self):
        response = self.client.post(url_for('auth.register'),data={
            'email':'john@example.com',
            'username':'john',
            'password':'cat',
            'password2':'cat'
        })
        self.assertTrue(response.status_code == 302) #实际网站是302，但是测试是200，搞不懂


        response = self.client.post(url_for('auth.login'),data={
            'email':'john@example.com',
            'password':'cat'
        },follow_redirects=True)  #follow_redirects自动向重定向的url发送GET请求
        self.assertTrue(re.search('Hello,\s+john',response.get_data(as_text=True)))
        self.assertTrue(b'You have not confirmed your account yet' in response.data)

        user = User.query.filter_by(email='john@example.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm',token=token),follow_redirects=True)
        self.assertTrue(b'You have confirmed your account' in response.data)


        response = self.client.get(url_for('auth.logout'),follow_redirects=True)
        self.assertTrue(b'You have been logged out' in response.data)