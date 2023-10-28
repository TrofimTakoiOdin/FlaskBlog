import unittest
from flask_blog.app.posts.forms import PostForm
from tests.common_setup import CommonSetup


class TestPostForm(unittest.TestCase, CommonSetup):
    def setUp(self):
        CommonSetup.setUp(self)

    def tearDown(self):
        CommonSetup.tearDown(self)

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
