import unittest
from flask import current_app
from app import create_app, db
from app.models import User
from datetime import datetime

class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_not_confirmed(self):
        test_user = User(username='sam', email="sam@gmail.com", password="sam",
            join_time=datetime.utcnow())
        db.session.add(test_user)
        db.session.commit()
        test = User.query.filter_by(username='sam').first()
        self.assertFalse(test.confirmed)

    def test_generate_token(self):
        test_user_1 = test_user = User(username='sam', email="sam@gmail.com", password="sam",
            join_time=datetime.utcnow())
        test_user_2 = User(username='dave', email="dave@gmail.com", password="dave",
            join_time=datetime.utcnow())
        db.session.add_all([test_user_1, test_user_2])
        db.session.commit()
        test_user_1 = User.query.filter_by(username='sam').first()
        test_user_2 = User.query.filter_by(username='dave').first()
        token_1 = test_user_1.generate_confirmation_token()
        token_2 = test_user_2.generate_confirmation_token()
        test_user_1.confirm(token_1)
        db.session.commit()
        test_user_1 = User.query.filter_by(username='sam').first()
        self.assertTrue(test_user_1.confirm(token_1))
        self.assertTrue(test_user_1.confirmed)
        self.assertFalse(token_1 == token_2)
