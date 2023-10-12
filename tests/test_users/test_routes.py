import unittest
from flask_blog.models import User
from tests.common_setup import CommonSetup


class TestRegisterRoute(unittest.TestCase, CommonSetup):

    def setUp(self):
        CommonSetup.setUp(self)

    def tearDown(self):
        CommonSetup.tearDown(self)

    def test_register_get(self):
        # Send a GET request to the register route
        response = self.client.get('/register')

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

    def test_register_post(self):
        # Generate a random test user using the test_utils method
        random_user, random_password = self.test_user, self.test_user_nonhashed_pwd

        # Send a POST request with the random user data
        data = {
            'username': random_user.username,
            'email': random_user.email,
            'password': random_password,
            'confirm_password': random_password
        }

        with self.app.test_request_context('/register', method='POST', data=data):
            # Establish a request context and send the POST request
            response = self.client.post('/register', data=data, follow_redirects=True)

            self.assertEqual(response.status_code, 200)

            # Check if the user is added to the database
        with self.app.app_context():
            user = User.query.filter_by(username=random_user.username).first()
            self.assertIsNotNone(user)


if __name__ == '__main__':
    unittest.main()
