from app import db


class Account(db.Model):
    """
    Account model.
    """

    id = db.Column('id', db.Integer, primary_key=True)
    screen_name = db.Column('screen_name', db.String(), nullable=False)
    email = db.Column('email', db.String(), nullable=False)
    password = db.Column('password', db.String(), nullable=False)
    phone_number = db.Column('phone_number', db.String(), nullable=False)
    status = db.Column('status', db.String())
    status_updated_at = db.Column('status_updated_at', db.DateTime())
