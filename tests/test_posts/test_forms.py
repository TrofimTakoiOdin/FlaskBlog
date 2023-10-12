import unittest
from flask_blog import create_app
from flask_blog.posts.forms import PostForm


class TestPostForm(unittest.TestCase):
    def setUp(self):
        # Create a Flask application context
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        # Pop the Flask application context after the test
        self.app_context.pop()

    def test_valid_data(self):
        # Create a PostForm instance with valid data
        form = PostForm(title="Test Title", content="This is a test content")

        # Ensure the form is valid
        self.assertTrue(form.validate())

    def test_missing_title(self):
        # Create a PostForm instance with a missing title
        form = PostForm(content="This is a test content")

        # Ensure the form is not valid
        self.assertFalse(form.validate())

    def test_missing_content(self):
        # Create a PostForm instance with missing content
        form = PostForm(title="Test Title")

        # Ensure the form is not valid
        self.assertFalse(form.validate())

    def test_empty_data(self):
        # Create a PostForm instance with empty data
        form = PostForm()

        # Ensure the form is not valid
        self.assertFalse(form.validate())

if __name__ == '__main__':
    unittest.main()
