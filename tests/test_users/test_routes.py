import unittest
from flask import request, get_flashed_messages
from flask_login import current_user
from flask_blog.models import User, Post
from tests.common_setup import CommonSetup
from tests.test_utils import get_test_user


class TestRegisterRoute(unittest.TestCase, CommonSetup):

    def setUp(self):
        CommonSetup.setUp(self)
        self.test_user, self.pwd = get_test_user(self.test_users)
        self.response = self.log_in_test_user(self.test_user, self.pwd)

    def tearDown(self):
        CommonSetup.tearDown(self)

    def test_register_get(self):
        # Send a GET request to the register route
        response = self.client.get('/register')

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

    def test_registeration(self):
        # Send a POST request with the random user data
        data = {
            'username': self.test_user.username,
            'email': self.test_user.email,
            'password': self.pwd,
            'confirm_password': self.pwd
        }

        with self.app.test_request_context('/register', method='POST', data=data):
            # Establish a request context and send the POST request
            response = self.client.post('/register', data=data, follow_redirects=True)

            self.assertEqual(response.status_code, 200)

            # Check if the user is added to the database
        with self.app.app_context():
            user = User.query.filter_by(username=self.test_user.username).first()
            self.assertIsNotNone(user)


class TestLoginRoute(unittest.TestCase, CommonSetup):
    def setUp(self):
        CommonSetup.setUp(self)
        self.test_user, self.pwd = get_test_user(self.test_users)

    def tearDown(self):
        CommonSetup.tearDown(self)

    def test_login_successful(self):
        with self.client:
            response = self.log_in_test_user(self.test_user, self.pwd)
            # Check if the user is authenticated and redirected to the home page
            self.assertTrue(current_user.is_authenticated)
            self.assertTrue(response.status_code == 302)  # Expect a redirect after successful login
            self.assertTrue(response.location == '/home')  # Check if it redirects to the home page

    def test_login_unsuccessful(self):
        # Set up the common test environment
        with self.client:
            response = self.client.post('/login', data={'email': self.test_user.email, 'password': 'wrongpassword'})
            self.assertTrue(response.status_code == 200)  # Expect a response without a redirect
            self.assertFalse(current_user.is_authenticated)

    class TestLogoutRoute(unittest.TestCase, CommonSetup):
        def setUp(self):
            CommonSetup.setUp(self)
            self.test_user, self.pwd = get_test_user(self.test_users)
            self.response = self.log_in_test_user(self.test_user, self.pwd)

        def tearDown(self):
            CommonSetup.tearDown(self)

        def test_logout(self):
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
        self.test_user, self.pwd = get_test_user(self.test_users)
        self.response = self.log_in_test_user(self.test_user, self.pwd)

    def tearDown(self):
        CommonSetup.tearDown(self)

    def test_account_get(self):
        with self.client:
            response = self.client.get('/account')

            # Check if the response status code is 200 (OK)
            self.assertEqual(response.status_code, 200)

    def test_account_update(self):
        with self.client:
            response = self.client.post('/account', data={'username': 'NewUsername', 'email': 'newemail@example.com'})

            # Check if the response status code is 302 (redirect)
            self.assertEqual(response.status_code, 302)

            # Check if the user's account was updated in the database
            updated_user = User.query.filter_by(email='newemail@example.com').first()
            self.assertEqual(updated_user.username, 'NewUsername')

    def test_account_route_unauthenticated(self):
        # Log out the test user (you may need to implement a logout route or method)
        self.client.get('/logout')

        # Try to access the account page while not logged in
        response = self.client.get('/account')

        # Check if the response status code is a redirect (e.g., 302 for a login page)
        self.assertEqual(response.status_code, 302)

        # You can also check if it redirects to the login page
        self.assertTrue(response.location.startswith('/login'))

    def test_profile_picture_upload(self):
        # Create a test image file to upload
        with open('../../flask_blog/static/profile_pics/default.jpg', 'rb') as image_data:
            # Make a POST request to upload the image
            with self.client as c:
                with c.session_transaction() as session:
                    session['_fresh'] = True  # Simulate a "fresh" session
                response = c.post('/account', data={'picture': (image_data, 'test_image.jpg')},
                                  content_type='multipart/form-data')

        # Check if the response status code is 200 (OK) indicating a successful upload
        self.assertEqual(response.status_code, 200)

        # Check if the user's image_file attribute has been updated in the database
        with self.app.app_context():
            email = self.test_user.email
            updated_user = User.query.filter_by(email=email).first()
            self.assertIsNotNone(updated_user.image_file)


class TestUserPostsRoute(unittest.TestCase, CommonSetup):

    def setUp(self):
        CommonSetup.setUp(self)

    def tearDown(self):
        CommonSetup.tearDown(self)

    def test_user_posts_route_basic(self):
        # Create a test user and add posts
        self.test_user, self.pwd = get_test_user(self.test_users)
        self.posts = []
        for i in range(5):
            post = Post(title=f'Test Post {i}', content=f'This is post {i}.', author=self.test_user)
            self.db.session.add(post)  # Use the session from CommonSetup
            self.posts.append(post)
        self.db.session.commit()

        with self.client:
            # Authenticate the user
            self.client.post('/login', data={'email': self.test_user.email, 'password': self.pwd})
            # Simulate a user accessing their posts using the session
            self.client.get(f'/user/{self.test_user.username}')

            # Check if the correct user's posts are displayed
            expected_path = f'/user/{self.test_user.username}'
            self.assertEqual(request.path, expected_path)
            self.assertTrue(current_user.is_authenticated)


class TestResetPasswordRequestRoute(unittest.TestCase, CommonSetup):
    def setUp(self):
        CommonSetup.setUp(self)

    def tearDown(self):
        CommonSetup.tearDown(self)

    def test_reset_password_request_route(self):
        # Create a test user and add them to the database
        self.test_user, self.pwd = get_test_user(self.test_users)
        self.db.session.commit()

        with self.client:
            # Simulate a user requesting a password reset
            data = {'email': self.test_user.email}
            response = self.client.post('/reset_password', data=data, follow_redirects=True)

            # Check if the response status code is 200 (OK)
            self.assertEqual(response.status_code, 200)

        # Check if the user is redirected to the login page after the reset request
        #     self.assertEqual(request.path, '/login')
        #     self.assertTrue(current_user.is_anonymous)

# Reset_token tests will appear soon


if __name__ == '__main__':
    unittest.main()
