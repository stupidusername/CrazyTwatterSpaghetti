from api.addvotepool import AddVotePool
from api.pollinfo import PollInfo
from api.votepoolinfo import VotePoolInfo
from createapp import create_app, db
from flask_admin import Admin
from flask_restful import Api
from models.account import Account
from views.accountview import AccountView
from views.importview import ImportView
from views.homeview import HomeView

# Create the app.
app = create_app()
# Push an application context to bind the SQLAlchemy object to your
# application.
app.app_context().push()

# Create app components.
api = Api(app)

# Initialize the admin interface.
admin = Admin(app, index_view=HomeView(url='/'))
admin.add_view(AccountView(Account, db.session, name='Accounts'))
admin.add_view(ImportView(name='Import CSV', endpoint='import'))

# Add API endpoints.
api.add_resource(
    AddVotePool,
    '/api/add-vote-pool/'
    '<int:tweet_id>/<int:option_index>/<int:intended_hits>/<int:max_tries>'
)
api.add_resource(
    PollInfo,
    '/api/poll-info/<int:tweet_id>'
)
api.add_resource(
    VotePoolInfo,
    '/api/vote-pool-info/<int:id>'
)
