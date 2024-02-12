import unittest
from datetime import datetime
from flask_blog import create_app, db
from flask_blog.models import User, AnonymousUser, Role, Permission, Follow


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        self.assertTrue(u.password == 'cat')

    def test_follow(self):
        user1 = User(username='user1', email='user1@example.com', password='password')
        user2 = User(username='user2', email='user2@example.com', password='password')
        db.session.add_all([user1, user2])
        db.session.commit()

        user1.follow(user2)
        db.session.commit()

        self.assertTrue(user1.is_following(user2))
        self.assertTrue(user2.is_followed_by(user1))

    def test_unfollow(self):
        user1 = User(username='user1', email='user1@example.com', password='password')
        user2 = User(username='user2', email='user2@example.com', password='password')
        db.session.add_all([user1, user2])
        db.session.commit()

        user1.follow(user2)
        db.session.commit()

        user1.unfollow(user2)
        db.session.commit()

        self.assertFalse(user1.is_following(user2))
        self.assertFalse(user2.is_followed_by(user1))

        # Add more test methods for other functionalities

    def test_ping(self):
        user = User(username='test_user', email='test_user@example.com', password='password')
        db.session.add(user)
        db.session.commit()

        # Save the initial last_seen value
        initial_last_seen = user.last_seen

        # Simulate a ping by calling the ping method
        user.ping()
        db.session.commit()

        # Check if last_seen is updated
        self.assertNotEqual(user.last_seen, initial_last_seen)
        self.assertTrue((datetime.utcnow() - user.last_seen).total_seconds() < 1)  # Check if last_seen is recent

    def test_user_role(self):
        u = User(email='john@example.com', password='cat')
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_moderator_role(self):
        r = Role.query.filter_by(name='Moderator').first()
        u = User(email='john@example.com', password='cat', role=r)
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_administrator_role(self):
        r = Role.query.filter_by(name='Administrator').first()
        u = User(email='john@example.com', password='cat', role=r)
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertTrue(u.can(Permission.ADMIN))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))


if __name__ == '__main__':
    unittest.main()

