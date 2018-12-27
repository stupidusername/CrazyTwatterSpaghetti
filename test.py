from createapp import create_app
import logging
from logging.handlers import RotatingFileHandler
from models.account import Account
from scrapers.twitterlogin import TwitterLogin

# Create a rotating log for errors.
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
handler = RotatingFileHandler('logs/faker.log', maxBytes=65536, backupCount=5)
logger.addHandler(handler)
# Also send errors to stderr.
logger.addHandler(logging.lastResort)

# Create the app.
app = create_app()
# Push an application context to bind the SQLAlchemy object to your
# application.
app.app_context().push()

# Process the accounts in batches.
limit = 25
min_id = 0
accounts = None
while accounts or accounts is None:
    # Get account models.
    accounts = Account.query.filter(Account.id > min_id).\
        order_by(Account.id.asc()).limit(limit).all()
    # Use the max id of this batch as the min id of the next one.
    if accounts:
        min_id = accounts[-1].id
    # Post a random status in the timeline of each account.
    for account in accounts:
        try:
            TwitterLogin(account)
        except Exception as e:
            logger.error(
                '"%s" login failed with exception: %s',
                account.screen_name,
                e
            )
