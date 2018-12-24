from createapp import db
from datetime import datetime
from typing import Optional


class Account(db.Model):
    """
    Account model.

    Status will be blank for those accounts which were not tested.

    :const str STATUS_LOGGED_IN: Login was successful.
    :const str STATUS_WRONG_CREDENTIALS: Incorrect screen name or password.
    :const str STATUS_SUSPENDED: Suspended account.
    :const str STATUS_UNCONFIRMED_ACCESS: A manual confirmation is needed.
    :const str STATUS_UNDETERMINED: Unable to complete the login process.
    """

    STATUS_LOGGED_IN = 'logged_in'
    STATUS_WRONG_CREDENTIALS = 'wrong_credentials'
    STATUS_SUSPENDED = 'suspended'
    STATUS_UNCONFIRMED_ACCESS = 'unconfirmed_access'
    STATUS_UNDETERMINED = 'undetermined'

    id = db.Column('id', db.Integer, primary_key=True)
    screen_name = \
        db.Column('screen_name', db.String(), nullable=False, unique=True)
    email = db.Column('email', db.String(), nullable=False, unique=True)
    password = db.Column('password', db.String(), nullable=False)
    phone_number = db.Column('phone_number', db.String(), nullable=False)
    status = db.Column('status', db.String())
    status_updated_at = db.Column('status_updated_at', db.DateTime())
    cookies = db.Column('cookies', db.Text())
    proxy = db.Column('proxy', db.String())

    def update_status(self, status: str):
        """
        Update status and status_updated_at fields.

        :param str status: New status.
        """
        self.status = status
        self.status_updated_at = datetime.utcnow()
        db.session.commit()

    def set_cookies(self, cookies: Optional[str]):
        """
        Set and save cookies.

        :param None | str cookies: Cookies.
        """
        self.cookies = cookies
        db.session.commit()
