import random
import string
from faker import Faker  # You may need to install the 'Faker' library

from flask_bcrypt import Bcrypt

from flask_blog import db, create_app
from flask_blog.models import User

fake = Faker()


def generate_random_string(length):
    """Generate a random string of the specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def create_random_test_user():
    """
    Create a random test user with a valid email, username, and password.

    :return: The created random test user.
    """
    bcrypt = Bcrypt()

    # Generate a random username, email, and password
    random_username = generate_random_string(8)  # You can adjust the length
    random_email = fake.email()
    random_password = generate_random_string(12)  # You can adjust the length
    image_file = 'flask_blog/static/profile_pics/9b25d2772b24e3e0.png'

    hashed_password = bcrypt.generate_password_hash(random_password).decode('utf-8')
    test_user = User(username=random_username, email=random_email, password=hashed_password, image_file=image_file)
    return test_user, random_password


def get_test_user(test_users: list):
    if test_users:
        user = test_users.pop()
        return user[0], user[1]  # tuple User and unhashed pwd
    else:
        return None, None
