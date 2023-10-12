import unittest
from flask import Flask, url_for
# from flask_bcrypt import Bcrypt
from flask_login import current_user
# from flask_sqlalchemy import SQLAlchemy
from flask_blog import create_app, db
from flask_blog.models import User, Post
# from flask_blog.config import TestingConfig
from tests import test_utils


class TestPostsBlueprint(unittest.TestCase):
    def setUp(self):
        self.app = create_app(environment='testing')
        self.client = self.app.test_client()
        self.db = db
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_user_data = test_utils.create_random_test_user()
        self.test_user_nonhashed_pwd = self.test_user_data[1]
        self.test_user = self.test_user_data[0]
        # Add the test user to the database
        db.create_all()
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login(self):
        with self.client:
            response = self.client.post('/login', data={'email': self.test_user.email, 'password': self.test_user_nonhashed_pwd})
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(response.status_code, 302)  # Expect a redirect after successful login
            self.assertEqual(response.location, url_for('main.home'))  # Check if it redirects to the home page

    def test_new_post(self):
        with self.client:
            # Log in the test user
            self.client.post('/login', data={'email': self.test_user.email, 'password': self.test_user_nonhashed_pwd})

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
            self.client.post('/login', data={'email': self.test_user.email, 'password': self.test_user_nonhashed_pwd})

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
            self.client.post('/login', data={'email': self.test_user.email, 'password': self.test_user_nonhashed_pwd})

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
