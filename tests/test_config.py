import os
import unittest
from flask import Flask
from flask_blog import create_app


class TestDevelopmentConfig(unittest.TestCase):
    def setUp(self):
        # Create a Flask app using the DevelopmentConfig
        self.app = create_app('development')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_development_config(self):
        # Test DevelopmentConfig settings
        self.assertEqual(self.app.config['SECRET_KEY'], os.environ.get('FLASK_SECRET_KEY'))
        self.assertEqual(self.app.config['SQLALCHEMY_DATABASE_URI'], os.environ.get('SQLALCHEMY_DB_URI'))
        self.assertEqual(self.app.config['MAIL_SERVER'], 'smtp.yandex.ru')
        self.assertEqual(self.app.config['MAIL_PORT'], 465)
        self.assertTrue(self.app.config['MAIL_USE_SSL'])
        self.assertEqual(self.app.config['MAIL_USERNAME'], os.environ.get('MAIL_DEV'))
        self.assertEqual(self.app.config['MAIL_PASSWORD'], os.environ.get('MAIL_DEV_PWD'))


if __name__ == '__main__':
    unittest.main()
