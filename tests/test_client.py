import unittest
from flask_blog import create_app, db
from flask_blog.app.users.forms import RegistrationForm
from flask_blog.models import User, Role

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Stranger' in response.get_data(as_text=True))

    def test_register_login(self):
        # Test registration with a new user
        with self.app.test_request_context('/register', method='POST'):
            data = {
                'username': 'testuser',
                'email': 'testuser@example.com',
                'password': 'testpassword',
                'confirm_password': 'testpassword',
            }

            form = RegistrationForm(data=data)

            # Ensure that the form is valid
            self.assertTrue(form.validate_on_submit())

            # Call the register route with the form data
            response = self.client.post('/register', data=data, follow_redirects=True)

            # Assertions
            self.assertEqual(response.status_code, 200)  # Assuming a successful registration redirects to the home page
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)  # Check if the user is in the database
            self.assertEqual(user.email, 'testuser@example.com')

            # Check if the user can log in after registration
            login_response = self.client.post('/login', data={'username': 'testuser', 'password': 'testpassword'},
                                              follow_redirects=True)

            # Additional assertions for login
            self.assertEqual(login_response.status_code, 200)  # Assuming a successful login redirects to the home page

    def test_register_route_with_existing_email(self):
        # Test registration with an existing email
        with self.app.test_request_context('/register', method='POST'):
            # Create a user with the existing email
            existing_user = User(username='newuser', email='existinguser@example.com', password='existingpassword')
            db.session.add(existing_user)
            db.session.commit()

            data = {
                'username': 'newuser',
                'email': 'existinguser@example.com',
                'password': 'testpassword',
                'confirm_password': 'testpassword',
            }

            form = RegistrationForm(data=data)

            # Ensure that the form validation catches the existing email
            self.assertFalse(form.validate_on_submit())
            self.assertIn('That email is taken. Please choose a different one.', form.errors['email'])



