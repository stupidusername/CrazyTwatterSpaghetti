from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
config = Config()
app.config['SQLALCHEMY_DATABASE_URI'] = config.get_sql_alchemy_url()
db = SQLAlchemy(app)

# Models can only be imported after db is declared.
from models.account import Account

@app.route("/")
def index():
    print(Account.query.all())
    return ':D'
