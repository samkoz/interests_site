# test relationships

import unittest
from flask import current_app
from app import create_app, db
from app.models import User, Entry, Tag
from datetime import datetime

class DatabaseTestCase(unittest.TestCase):
    # this is run before each test method to create the testing environment
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        u = User(username='sam', email="me@gmail.com", password='test', join_time=datetime.utcnow())
        e1 = Entry(entry="e1", entry_time=datetime.utcnow(), user=u)
        e2 = Entry(entry="e2", entry_time=datetime.utcnow(), user=u)
        t1 = Tag(tag="t1")
        t2 = Tag(tag="t2")
        # add it to the database
        db.session.add_all([u, e1, t1, t2])

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_to_db(self):
        """test user is in db"""
        u = User.query.filter(User.username=="sam")[0]
        self.assertTrue(u.username == "sam")

    def test_change_username(self):
        """test changing username"""
        u = User.query.first()
        u.username = "change"
        db.session.add(u)
        db.session.commit()
        u = User.query.first()
        self.assertTrue(u.username == "change")

    def test_delete_user(self):
        """test deleting a user"""
        user = User.query.first()
        db.session.delete(user)
        db.session.commit()
        none_user = User.query.first()
        self.assertTrue(none_user == None)

    def test_add_entry(self):
        """test adding an entry"""
        u = User.query.first()
        e = Entry.query.first()
        self.assertTrue(e == u.entries[0])

    def test_add_tags(self):
        """add a tag to an entry"""
        e = Entry.query.first()
        t = Tag.query.first()
        e.tags.append(t)
        db.session.add_all([e,t])
        db.session.commit()
        e = Entry.query.first()
        test_tag = e.tags[0].tag
        self.assertTrue(test_tag == t.tag)

    def test_muti_tag(self):
        """add mutiple tags to an entry"""
        e = Entry.query.first()
        tags = Tag.query.all()

        for tag in tags:
            e.tags.append(tag)
        db.session.add(e)
        db.session.commit()
        e = Entry.query.first()
        tags = e.tags.count()
        self.assertTrue(tags == 2)
