# commands/users_crud_cli.py
import click
from flask import Blueprint
from flask.cli import with_appcontext
from flask_blog import db, bcrypt
from flask_blog.commands.utils import get_non_empty_value, get_user_by_id_or_username
from flask_blog.models import User

users_crud = Blueprint('users_crud', __name__)


@users_crud.cli.command("create_confirmed_user")
@click.option("--username", prompt=True)
@click.option("--email", prompt=True)
@click.password_option("--password", confirmation_prompt=True)
@with_appcontext
def create_confirmed_user(username, email, password):
    """
    Create a confirmed user.

    This command prompts the user to enter the necessary information for creating a new confirmed user.
    The user will be asked to provide a unique username, a valid email address, and a secure password.

    Examples:
    - flask users_crud create_confirmed_user
    - flask users_crud create_confirmed_user --username=johndoe --email=johndoe@example.com --password=securepassword
    """
    # Prompt for each parameter separately
    username = get_non_empty_value(username, "Enter username")
    email = get_non_empty_value(email, "Enter email")
    password = get_non_empty_value(password, "Enter password", is_password=True)

    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password, confirmed=True)
        db.session.add(new_user)
        db.session.commit()
        success_message = click.style(f"Confirmed user {username} created successfully! Email: {email}", fg="green")
        click.echo(success_message)

    except Exception as e:
        db.session.rollback()
        error_message = click.style(f"Error creating user: {e}", fg="red")
        click.echo(error_message)


@users_crud.cli.command("update_user")
@click.argument("username", type=str)
@with_appcontext
def update_user(username):
    """
    Update a user.

    This command allows you to update various details for a user identified by their username.
    You will be prompted to choose which information to update, including username, email, and password.

    Usage:
    flask users_crud update_user <username>

    Example:
    flask users_crud update_user --username=johndoe

    Options:
    1) Update username
    2) Update email
    3) Update password
    4) Update username, email, and password

    Upon choosing an option, you will be prompted to enter the new information.
    The changes made to the user will be displayed upon successful update.

    """
    user = User.query.filter_by(username=username).first()
    while not user:
        username = click.prompt("Enter VALID USERNAME of the user you want to update", type=str)
        user = User.query.filter_by(username=username).first()

        if not user:
            error_message = click.style(f"User with username {username} not found.", fg="red")
            click.echo(error_message)
            username = ""  # Reset username to enter the loop again

    click.echo(f"Choose what to update for user {username}:")

    options = {
        "1": "Update username",
        "2": "Update email",
        "3": "Update password",
        "4": "Update username, email, and password",
    }
    changes = []

    while True:
        for key, value in options.items():
            click.echo(f"{key}) {value}")

        choice = click.prompt("Enter your choice", type=str)

        if choice in options:
            break

        click.echo("Invalid choice. Please select a valid option.")

    if choice == "1":
        old_username = user.username
        new_username = click.prompt("Enter new username", type=str, default=user.username)
        user.username = new_username
        changes.append(f"username changed from {old_username} to {new_username}")
    elif choice == "2":
        old_email = user.email
        new_email = click.prompt("Enter new email", type=str, default=user.email)
        user.email = new_email
        changes.append(f"email changed from {old_email} to {new_email}")
    elif choice == "3":
        new_password = click.prompt("Enter new_password", hide_input=True, confirmation_prompt=True)
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password = hashed_password
        changes.append("password changed")
    elif choice == "4":
        old_username, old_email = user.username, user.email
        new_username = click.prompt("Enter new username", type=str, default=user.username)
        new_email = click.prompt("Enter new email", type=str, default=user.email)
        new_password = click.prompt("Enter new_password", hide_input=True, confirmation_prompt=True)
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.username = new_username
        user.email = new_email
        user.password = hashed_password
        changes.append(f"username changed from {old_username} to {new_username}")
        changes.append(f"email changed from {old_email} to {new_email}")
        changes.append("password changed")

    try:
        db.session.commit()
        success_message = click.style(f"You updated user {username}. You changed: {', '.join(changes)}.", fg="green")
        click.echo(success_message)

    except Exception as e:
        db.session.rollback()
        error_message = click.style(f"Error updating user: {e}", fg="red")
        click.echo(error_message)


@users_crud.cli.command("delete_user")
@click.argument("identifier", type=click.STRING)
@with_appcontext
def delete_user(identifier):
    """
    Delete a user by ID or username.

    This command allows you to delete a user identified by their ID or username.
    You will be prompted to confirm the deletion before the operation is executed.

    Usage:
    flask users_crud delete_user <identifier>

    Example:
    flask users_crud delete_user --identifier=johndoe

    Options:
    - identifier: The ID or username of the user to be deleted.

    Upon successful deletion, a confirmation message will be displayed.

    """

    user = get_user_by_id_or_username(identifier)
    if not user:
        message = click.style("There is no such user!", fg='red')
        click.echo(message)
        return
    try:
        db.session.delete(user)
        db.session.commit()
        success_message = click.style(f"User '{user.username}' deleted successfully!", fg="green")
        click.echo(success_message)

    except Exception as e:
        db.session.rollback()
        error_message = click.style(f"Error deleting user: {e}", fg="red")
        click.echo(error_message)
