from config import Config
from flask import Flask
from flask_admin import Admin
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import InternalServerError

# Create and configure app.
app = Flask(__name__)
config = Config()
app.config['SECRET_KEY'] = config.get_secret_key()
app.config['SQLALCHEMY_DATABASE_URI'] = config.get_sql_alchemy_url()

# Register error handlers.
@app.errorhandler(InternalServerError)
def handle_bad_request(e):
    return str(e), InternalServerError.code

# Create app components.
api = Api(app)
# Variable db must be declared before the rest of the imported classes use it.
db = SQLAlchemy(app)

# Import models.
from models.account import Account

# Import views.
from views.accountview import AccountView
from views.importview import ImportView
from views.homeview import HomeView

# Initialize the admin interface.
admin = Admin(app, index_view=HomeView(url='/'))
admin.add_view(AccountView(Account, db.session, name='Accounts'))
admin.add_view(ImportView(name='Import CSV', endpoint='import'))

# Import api resources.
from api.pollinfo import PollInfo
from api.pollvote import PollVote

# Add API endpoints.
api.add_resource(
    PollInfo,
    '/api/poll-info/<int:tweet_id>'
)
api.add_resource(
    PollVote,
    '/api/poll-vote/<int:tweet_id>/<int:option_index>/<int:votes>'
)
