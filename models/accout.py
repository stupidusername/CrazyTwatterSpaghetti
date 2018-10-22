from app import db


class Account(db.Model):
    """
    Account model.
    """

    id = db.Column('id', db.Integer, primary_key=True)
    screen_name = db.Column('screen_name', db.String())
    email = db.Column('email', db.String())
    password = db.Column('password', db.String())
    phone_number = db.Column('phone_number', db.String())
    status = db.Column('status', db.String())
    status_updated_at = db.Column('status_updated_at', db.DateTime())
