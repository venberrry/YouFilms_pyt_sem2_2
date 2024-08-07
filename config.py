import os
basedir = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.urandom(32)
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:12345asd@localhost/YFpython'
SESSION_TYPE = 'filesystem'
UPLOAD_FOLDER = 'users_photos'
WTF_CSRF_ENABLED = True


'''
Данные для Flask-MAIL
'''
MAIL_SERVER = 'smtp.yandex.ru'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'yashma.cats@yandex.ru'
MAIL_PASSWORD = 'bmclafetzydcytgu'