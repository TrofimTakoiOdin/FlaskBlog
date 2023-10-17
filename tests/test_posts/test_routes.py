import unittest
from flask import url_for
from flask_login import current_user
from flask_blog import db
from flask_blog.models import Post
from tests.common_setup import CommonSetup
from tests.test_utils import get_test_user


class TestPostsBlueprint(unittest.TestCase, CommonSetup):

    def setUp(self):
        CommonSetup.setUp(self)
        self.test_user, self.pwd = get_test_user(self.test_users)

    def tearDown(self):
        CommonSetup.tearDown(self)

    def test_login(self):
        with self.client:
            self.response = self.log_in_test_user(self.test_user, self.pwd)
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(self.response.status_code, 302)  # Expect a redirect after successful login
            self.assertEqual(self.response.location, url_for('main.home'))  # Check if it redirects to the home page

    def test_new_post(self):
        with self.client:
            # Log in the test user
            self.log_in_test_user(self.test_user, self.pwd)

            # Make a POST request to create a new post
            response = self.client.post('/post/new', data={'title': 'Test Post', 'content': 'This is a test post'})

            # Check if the post was created successfully
            self.assertEqual(response.status_code, 302)  # Expect a redirect
            self.assertEqual(response.location, url_for('main.home'))  # Check if it redirects to the home page

            # Check if the post exists in the database
            post = Post.query.filter_by(title='Test Post').first()
            self.assertIsNotNone(post)
            self.assertEqual(post.title, 'Test Post')
            self.assertEqual(post.content, 'This is a test post')
            self.assertEqual(post.author, current_user)

            # Make a GET request to view the test post
            response = self.client.get(f'/post/{post.id}')

            # Check if the response status code is 200 (OK)
            self.assertEqual(response.status_code, 200)

            # Check if the post's title is present in the rendered HTML
            self.assertIn(post.title.encode(), response.data)

            # Check if the post's content is present in the rendered HTML
            self.assertIn(post.content.encode(), response.data)

    def test_update_post(self):
        test_user = self.test_user
        with self.client:
            self.log_in_test_user(self.test_user, self.pwd)
            # Create a test post
            test_post = Post(title='Test Post', content='This is a test post', author=test_user)
            db.session.add(test_post)
            db.session.commit()

            # Make a GET request to view the edit post page
            response = self.client.get(f'/post/{test_post.id}/update')

            # Check if the response status code is 200 (OK)
            self.assertEqual(response.status_code, 200)

            # Create a POST request to update the post
            updated_title = 'Updated Test Post'
            updated_content = 'This is the updated content of the test post'
            response = self.client.post(f'/post/{test_post.id}/update',
                                        data={'title': updated_title, 'content': updated_content})

            # Check if the response status code is 302 (redirect)
            self.assertEqual(response.status_code, 302)

            # Check if the post's title and content were updated in the database
            updated_post = Post.query.get(test_post.id)
            self.assertEqual(updated_post.title, updated_title)
            self.assertEqual(updated_post.content, updated_content)

    def test_delete_post(self):
        test_user = self.test_user
        with self.client:
            self.log_in_test_user(self.test_user, self.pwd)

            # Create a test post and add it to the database
            test_post = Post(title='Test Post', content='This is a test post', author=test_user)
            db.session.add(test_post)
            db.session.commit()

            # Make a POST request to delete the test post
            response = self.client.post(f'/post/{test_post.id}/delete')

            # Check if the response status code is 302 (redirect)
            self.assertEqual(response.status_code, 302)

            # Check if the test post was deleted from the database
            deleted_post = Post.query.get(test_post.id)
            self.assertIsNone(deleted_post)


if __name__ == '__main__':
    unittest.main()
