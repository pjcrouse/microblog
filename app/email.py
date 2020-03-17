from flask import current_app
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
    Thread(target=send_async_email, args=(current_app._get_current_object(), destination, message, sender)).start()
