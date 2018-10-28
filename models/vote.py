from app import db


class Vote(db.Model):
    """
    Vote model.
    """

    id = db.Column('id', db.Integer, primary_key=True)
    vote_pool_id = db.Column(
        'vote_pool_id',
        db.Integer,
        db.ForeignKey('vote_pool.id'),
        nullabe=False
    )
    create_datetime = \
        db.Column('create_datetime', db.DateTime(), nullable=False)
    screen_name = \
        db.Column('screen_name', db.String(), nullable=False, unique=True)
    email = db.Column('email', db.String(), nullable=False, unique=True)
    password = db.Column('password', db.String(), nullable=False)
    phone_number = db.Column('phone_number', db.String(), nullable=False)
    hit = db.Column('hit', db.Boolean)
    error = db.Column('error', db.Text())
