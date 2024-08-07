from flask_session.__init__ import Session
from flask import Flask, session as just_session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_socketio import SocketIO
from SupChat import MySocket

app = Flask(__name__)
app.config.from_object('config')

Session(app)

db = SQLAlchemy(app)
mail = Mail(app)
socketio = MySocket(app)

from views import *

if __name__ == '__main__':
    app.debug = True
    with app.app_context():
        app.run()
