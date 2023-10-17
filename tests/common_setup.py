from flask import session

from flask_blog import create_app, db
from tests import test_utils

class CommonSetup:
    def __init__(self):
        self.NUM_OF_USERS = None
        self.test_users = None
        self.app = None
        self.client = None
        self.db = None
        self.app_context = None

    def setUp(self):
        # Create a test app and client
        self.app = create_app(environment='testing')
        self.client = self.app.test_client()
        self.db = db
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.NUM_OF_USERS = 10  # We can change it later

        self.test_users = []  # List to store test users

        # Create and add test users to the database
        for _ in range(self.NUM_OF_USERS):
            user, password = test_utils.create_random_test_user()
            db.session.add(user)
            self.test_users.append((user, password))

        db.create_all()
        db.session.commit()

    def log_in_test_user(self, user, password):
        response = self.client.post('/login', data={'email': user.email, 'password': password})
        return response

    def has_open_session(self):
        with self.app.app_context():
            return 'user_id' in session

    def tearDown(self):
        # Clean up the test database
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
