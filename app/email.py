from flask_mail import Message
from app import mail, app
from flask import render_template
from threading import Thread
import boto3


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    client = boto3.client('ses')
    CHARSET = 'UTF-8'
    response = client.send_email(
        Destination={'ToAddresses': recipients},
        Message={
            'Body': {
                'Html': {
                    'Charset': CHARSET,
                    'Data': html_body,
                },
                'Text': {
                    'Charset': CHARSET,
                    'Data': text_body,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': subject + 'Sent From AWS',
            },
        },
        Source=sender)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Quarantogether] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))
