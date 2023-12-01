import unittest
from unittest.mock import patch

import click
from click.testing import CliRunner

from flask_blog import create_app, db
from flask_blog.models import User
from flask_blog.commands.users_crud_cli import create_confirmed_user, users_crud, update_user, delete_user
from flask_blog import bcrypt


class TestUsersCRUDCommand(unittest.TestCase):

    def setUp(self):
        # Create a Flask app with the testing configuration
        self.app = create_app('testing')



        self.db = db
        self.app.app_context().push()

        # Initialize bcrypt
        bcrypt.init_app(self.app)

        # Create tables in the test database
        self.db.create_all()

    def tearDown(self):
        # Drop all tables after each test
        self.db.session.remove()
        self.db.drop_all()

    def test_create_confirmed_user(self):
        # Create a Click runner for testing
        runner = CliRunner()

        # Mock user input
        user_input = 'testuser\ntestuser@example.com\ntestpassword\ntestpassword\n'

        # Run the command and capture the result
        result = runner.invoke(create_confirmed_user, input=user_input)

        # Check the exit code and output
        self.assertEqual(result.exit_code, 0)  # Assuming 0 is the expected exit code for success
        self.assertIn('Confirmed user testuser created successfully!', result.output)

        # Retrieve the user from the database
        created_user = User.query.filter_by(username='testuser').first()

        # Assert that the user was created and has the correct attributes
        self.assertIsNotNone(created_user)
        self.assertEqual(created_user.username, 'testuser')
        self.assertEqual(created_user.email, 'testuser@example.com')
        self.assertTrue(bcrypt.check_password_hash(created_user.password, 'testpassword'))
        self.assertTrue(created_user.confirmed)

    def test_update_user(self):
        def test_update_user_with_different_inputs(self):
            # Create a Click runner for testing
            runner = CliRunner()

            # Create a user for testing
            test_user = User(username='testuser', email='testuser@example.com', password='testpassword')
            self.db.session.add(test_user)
            self.db.session.commit()

            # Define different user inputs to test
            input_cases = [
                ('1\nnewusername\n', 'username changed from testuser to newusername'),
                ('2\nnewemail@example.com\n', 'email changed from testuser@example.com to newemail@example.com'),
                ('3\ntestpassword\n', 'password changed'),
                ('4\nnewusername\nnewemail@example.com\ntestpassword\n',
                 'username changed from testuser to newusername, email changed from testuser@example.com to '
                 'newemail@example.com, password changed'),
            ]

            # Run the command for each input case
            for user_input, expected_output in input_cases:
                with self.subTest(user_input=user_input):
                    # Run the command and capture the result
                    result = runner.invoke(update_user, ['testuser'], input=user_input)

                    # Check the exit code and output
                    self.assertEqual(result.exit_code, 0)  # Assuming 0 is the expected exit code for success
                    self.assertIn(f'You updated user testuser. You changed: {expected_output}', result.output)

    def test_delete_user(self):
        # Create a Click runner for testing
        runner = CliRunner()

        # Create a user for testing
        test_user = User(username='testuser', email='testuser@example.com', password='testpassword')
        self.db.session.add(test_user)
        self.db.session.commit()

        # Test case 1: Successful deletion
        result = runner.invoke(delete_user, ['testuser'])
        self.assertEqual(result.exit_code, 0)  # Assuming 0 is the expected exit code for success
        self.assertIn('User \'testuser\' deleted successfully!', result.output)

        # Test case 2: Attempt to delete a non-existent user
        result = runner.invoke(delete_user, ['nonexistentuser'])
        self.assertEqual(result.exit_code, 0)  # Assuming 0 is the expected exit code for success
        self.assertIn("There is no such user!", result.output)


if __name__ == '__main__':
    unittest.main()
