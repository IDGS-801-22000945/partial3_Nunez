from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from config import DevelopmentConfig
import os
import datetime

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)


login_manager = LoginManager()
login_manager.login_view = "login"  
login_manager.init_app(app)

db = SQLAlchemy(app)

from routes import *
from models import Cliente, Pedido, User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == "__main__":
    app.run(debug=True)