from createapp import create_app
import datetime
from generators import status
import logging
from logging.handlers import RotatingFileHandler
from models.account import Account
from scrapers.twitterlogin import TwitterLogin
from scrapers.twitterstatusupdate import TwitterStatusUpdate
from sqlalchemy import or_

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


def _get_date_seven_days_ago() -> datetime.date:
    """
    Get date 7 days ago.
    :returns: A date object.
    """
    now = datetime.datetime.utcnow()
    seven_days_ago = now - datetime.timedelta(days=7)
    date_seven_days_ago = seven_days_ago.date()
    return date_seven_days_ago


# Process the accounts in batches.
limit = 25
min_id = 0
accounts = None
while accounts or accounts is None:
    # Select accounts that where not tried out yet or were logged in for the
    # last time over a week ago.
    accounts = Account.query.filter(
        or_(
            Account.status.is_(None),
            Account.status == Account.STATUS_LOGGED_IN
        ),
        or_(
            Account.status_updated_at.is_(None),
            Account.status_updated_at <= _get_date_seven_days_ago()
        ),
        Account.id > min_id
    ).order_by(Account.id.asc()).limit(limit).all()
    # Use the max id of this batch as the min id of the next one.
    if accounts:
        min_id = accounts[-1].id
    # Post a random status in the timeline of each account.
    for account in accounts:
        try:
            TwitterStatusUpdate(TwitterLogin(account), status.get_random())
        except Exception as e:
            logger.error(
                '"%s" status update failed with exception: %s',
                account.screen_name,
                e
            )
