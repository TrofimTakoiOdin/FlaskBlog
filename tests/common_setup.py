from flask_blog import create_app, db
from tests.test_utils import create_random_test_user


class CommonSetup:
    def __init__(self):
        self.app = None
        self.client = None
        self.db = None
        self.app_context = None
        self.test_user_data = None
        self.test_user_nonhashed_pwd = None
        self.test_user = None

    def setUp(self):

        # Create a test app and client
        self.app = create_app(environment='testing')
        self.client = self.app.test_client()
        self.db = db
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_user_data = create_random_test_user()
        self.test_user_nonhashed_pwd = self.test_user_data[1]
        self.test_user = self.test_user_data[0]

        # Add the test user to the database
        db.create_all()
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        # Clean up the test database
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
