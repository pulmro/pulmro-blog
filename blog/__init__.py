from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_pagedown import PageDown
from flask_login import LoginManager
from flask_bcrypt import Bcrypt



app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
loginmanager = LoginManager()
loginmanager.init_app(app)
bcrypt = Bcrypt(app)
pagedown = PageDown(app)

from blog import views, models
