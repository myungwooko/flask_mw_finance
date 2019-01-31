from flask import Flask
from db_config import config


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{config['username']}:{config['password']}@localhost/mw_finance"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JSON_SORT_KEYS"] = False
app.config['SECRET_KEY'] = 'thisissecret'