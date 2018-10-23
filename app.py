from config import Config
from flask import Flask
from flask_admin import Admin, AdminIndexView
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import InternalServerError

app = Flask(__name__)
config = Config()
app.config['SECRET_KEY'] = config.get_secret_key()
app.config['SQLALCHEMY_DATABASE_URI'] = config.get_sql_alchemy_url()
db = SQLAlchemy(app)

# Models can only be imported after db is declared.
from models.account import Account

# Import views.
from views.accountview import AccountView
from views.importview import ImportView
from views.homeview import HomeView

# Register error handlers.
@app.errorhandler(InternalServerError)
def handle_bad_request(e):
    return str(e), InternalServerError.code

# Initialize the admin interface.
admin = Admin(app, index_view=HomeView(url='/'))
admin.add_view(AccountView(Account, db.session, name='Accounts'))
admin.add_view(ImportView(name='Import CSV', endpoint='import'))
