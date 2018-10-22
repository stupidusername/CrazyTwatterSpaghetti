from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
config = Config()
app.config['SQLALCHEMY_DATABASE_URI'] = config.get_sql_alchemy_url()
db = SQLAlchemy(app)

@app.route("/")
def index():
    return "Hello World!"
