from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from haadupkg import config

app = Flask(__name__,instance_relative_config=True)
app.config.from_pyfile('config.py')
app.config.from_object(config.LiveConfig)
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)

from haadupkg.routes import user_routes, admin_routes, products_routes,vendor_routes

from haadupkg import models,forms
