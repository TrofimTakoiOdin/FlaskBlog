import unittest
from flask import url_for
from flask_blog import create_app, db
from flask_blog.models import Post
from tests.common_setup import CommonSetup


class TestMainRoutes(unittest.TestCase, CommonSetup):

    def setUp(self):
        CommonSetup.setUp(self)


        # Add test data to the database
        post1 = Post(title='Test Post 1', content='Content of Test Post 1', author=self.test_user)
        post2 = Post(title='Test Post 2', content='Content of Test Post 2', author=self.test_user)
        db.session.add(post1)
        db.session.add(post2)
        db.session.commit()

    def tearDown(self):
        CommonSetup.tearDown(self)

    def test_home_route(self):
        with self.app.test_request_context():
            response = self.client.get(url_for('main.home'))
            self.assertEqual(response.status_code, 200)  # Ensure a successful response
            self.assertIn(b'Test Post 1', response.data)  # Check if post content is in the response

    def test_about_route(self):
        with self.app.test_request_context():
            response = self.client.get(url_for('main.about'))
            self.assertEqual(response.status_code, 200)  # Ensure a successful response
            self.assertIn(b'About', response.data)  # Check if "About" is in the response


if __name__ == '__main__':
    unittest.main()
