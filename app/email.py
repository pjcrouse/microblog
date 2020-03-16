from flask_mail import Message
from app import mail, app
from flask import render_template
from threading import Thread
import boto3


def send_async_email(app, destination, message, sender):
    with app.app_context():
        client = boto3.client('ses')
        client.send_email(Destination=destination, Message=message, Source=sender)


def send_email(subject, sender, recipients, text_body, html_body):
    client = boto3.client('ses')
    charset = 'UTF-8'
    destination = {'ToAddresses': recipients}
    message = {
            'Body': {
                'Html': {
                    'Charset': charset,
                    'Data': html_body,
                },
                'Text': {
                    'Charset': charset,
                    'Data': text_body,
                },
            },
            'Subject': {
                'Charset': charset,
                'Data': subject,
            },
        }
    Thread(target=send_async_email, args=(app, destination, message, sender)).start()


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[QuaranTogether] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))
