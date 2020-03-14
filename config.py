import os

class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-super-secrete-key-nobody-will-ever-guess'
