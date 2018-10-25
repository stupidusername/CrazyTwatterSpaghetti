from app import db


class Account(db.Model):
    """
    Account model.

    Status will be blank for those account which were not tested or were not
    able to complete a login process.

    :const str LOGGED_IN: Login was successful.
    :const str WRONG_CREDENTIALS: Incorrect screen name or password.
    :const str SUSPENDED: Suspended account.
    :const str UNCONFIRMED_ACCESS: A manual confirmation is needed.
    """

    STATUS_LOGGED_IN = 'logged_in'
    STATUS_WRONG_CREDENTIALS = 'wrong_credentials'
    STATUS_SUSPENDED = 'suspended'
    STATUS_UNCONFIRMED_ACCESS = 'unconfirmed_acess'

    id = db.Column('id', db.Integer, primary_key=True)
    screen_name = \
        db.Column('screen_name', db.String(), nullable=False, unique=True)
    email = db.Column('email', db.String(), nullable=False, unique=True)
    password = db.Column('password', db.String(), nullable=False)
    phone_number = db.Column('phone_number', db.String(), nullable=False)
    status = db.Column('status', db.String())
    status_updated_at = db.Column('status_updated_at', db.DateTime())
