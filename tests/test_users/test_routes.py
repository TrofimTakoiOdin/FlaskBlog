import unittest
from flask_login import current_user
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


class TestLoginRoute(unittest.TestCase, CommonSetup):
    def setUp(self):
        CommonSetup.setUp(self)

    def tearDown(self):
        CommonSetup.tearDown(self)

    def test_login_successful(self):
        # Set up the common test environment

        with self.client:
            response = self.client.post('/login',
                                        data={'email': self.test_user.email, 'password': self.test_user_nonhashed_pwd})

            # Check if the user is authenticated and redirected to the home page
            self.assertTrue(current_user.is_authenticated)
            self.assertTrue(response.status_code == 302)  # Expect a redirect after successful login
            self.assertTrue(response.location == '/home')  # Check if it redirects to the home page

    def test_login_unsuccessful(self):
        # Set up the common test environment

        with self.client:
            response = self.client.post('/login', data={'email': self.test_user.email, 'password': 'wrongpassword'})

            # Check if the login is unsuccessful (no need to check flashed messages)
            self.assertTrue(response.status_code == 200)  # Expect a response without a redirect
            self.assertFalse(current_user.is_authenticated)

    class TestLogoutRoute(unittest.TestCase, CommonSetup):
        def setUp(self):
            CommonSetup.setUp(self)

        def tearDown(self):
            CommonSetup.tearDown(self)

        def test_logout(self):
            self.client.post('/login', data={'email': self.test_user.email, 'password': self.test_user_nonhashed_pwd})
            self.assertTrue(current_user.is_authenticated)

            with self.client:
                response = self.client.get('/logout')

                # Check if the user is logged out and redirected to the home page
                self.assertFalse(current_user.is_authenticated)
                self.assertTrue(response.status_code == 302)  # Expect a redirect after logout
                self.assertTrue(response.location == '/home')  # Check if it redirects to the home page


class TestAccountRoute(unittest.TestCase, CommonSetup):
    def setUp(self):
        CommonSetup.setUp(self)
        # Log in the test user
        self.client.post('/login', data={'email': self.test_user.email, 'password': self.test_user_nonhashed_pwd})

    def tearDown(self):
        CommonSetup.tearDown(self)

    def test_account_get(self):

        with self.client:
            response = self.client.get('/account')

            # Check if the response status code is 200 (OK)
            self.assertEqual(response.status_code, 200)

    def test_account_post(self):

        with self.client:
            response = self.client.post('/account', data={'username': 'NewUsername', 'email': 'newemail@example.com'})

            # Check if the response status code is 302 (redirect)
            self.assertEqual(response.status_code, 302)

            # Check if the user's account was updated in the database
            updated_user = User.query.filter_by(email='newemail@example.com').first()
            self.assertEqual(updated_user.username, 'NewUsername')


if __name__ == '__main__':
    unittest.main()
