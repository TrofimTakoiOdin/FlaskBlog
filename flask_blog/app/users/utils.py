import os
import secrets
from flask_blog.config import Config
from PIL import Image
from flask import url_for, current_app
import smtplib
from email.mime.text import MIMEText

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    output_size = (256, 256)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    body = f'''To reset your password, visit the following link:
     {url_for('users.reset_token', token=token, _external=True)}
     If you did not make this request then simply ignore this email and no changes will be made.'''
    sender = Config.MAIL_USERNAME
    recipients = [user.email]
    password = Config.MAIL_PASSWORD
    msg = MIMEText(body)
    msg['Subject'] = "Reset password request"
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    with smtplib.SMTP_SSL('smtp.gmail.com', Config.MAIL_PORT) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())

    # msg = Message('Password Reset Request',
    #               sender='projects.trofimov@gmail.com',
    #               recipients=[user.email])
    # msg.body = f'''To reset your password, visit the following link:
    # {url_for('users.reset_token', token=token, _external=True)}
    #
    # If you did not make this request then simply ignore this email and no changes will be made.
    # '''
    # mail.send(msg)


def send_confirmation_email(user, token):
    user, token = user, token
    body = f'''To CONFIRM your account, visit the following link:
    {url_for('users.confirm', token=token, _external=True)}

    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    sender = Config.MAIL_USERNAME
    recipients = [user.email]
    password = Config.MAIL_PASSWORD
    msg = MIMEText(body)
    msg['Subject'] = "Confirm your account"
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', Config.MAIL_PORT) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())

