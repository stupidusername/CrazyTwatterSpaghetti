from config import Config
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
config = Config()
app.config['SQLALCHEMY_DATABASE_URI'] = config.get_sql_alchemy_url()
db = SQLAlchemy(app)

# Models can only be imported after db is declared.
from models.account import Account

# Initialize the admin interface.
admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
admin.add_view(ModelView(Account, db.session))

@app.route("/")
def index():
    print(Account.query.all())
    return ':D'
