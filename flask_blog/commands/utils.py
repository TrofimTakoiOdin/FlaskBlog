import click

from flask_blog.models import User


def get_non_empty_value(parameter_name, prompt_text, is_password=False):
    """
        Prompt the user for a non-empty value.

        This function is used to get a non-empty value for a specified parameter.
        If the parameter is flagged as a password, the input will be hidden.

        Parameters:
        - parameter_name (str): The value to be obtained.
        - prompt_text (str): The prompt text displayed to the user.
        - is_password (bool): Flag indicating whether the value is a password.

        Returns:
        str: The non-empty value entered by the user.

        """
    while not parameter_name:
        if is_password:
            parameter_name = click.password_option("Password can't be empty", confirmation_prompt=True)
        else:
            parameter_name = click.prompt(prompt_text, type=str, default="")
        if not parameter_name:
            click.echo(f"{prompt_text.capitalize()} is required. Please try again.")
    return parameter_name


def get_user_by_id_or_username(identifier):
    """
    Helper function to get a user by ID or username.

    This function takes an identifier, checks if it is a digit (indicating an ID),
    and retrieves the corresponding user. If the identifier is a non-numeric string,
    it searches for the user by username.

    Parameters:
    - identifier (str): The ID or username of the user to be retrieved.

    Returns:
    User or None: The User object if a valid user is found, else None.

    """

    if identifier.isdigit():
        identifier = int(identifier)
        user = User.query.get(identifier)
    else:
        user = User.query.filter_by(username=identifier).first()

    return user
