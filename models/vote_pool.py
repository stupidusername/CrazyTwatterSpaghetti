from app import db


class VotePool(db.Model):
    """
    Vote pool model.

    :const str STATUS_RUNNING: The vote pool is running.
    :const str STATUS_FINISHED: The vote pool has finished.
    :const str STATUS_INTERRUPTED: The vote pool could not finish.
    """

    STATUS_RUNNING = 'running'
    STATUS_FINISHED = 'finished'
    STATUS_INTERRUPTED = 'interrupted'

    id = db.Column('id', db.Integer, primary_key=True)
    tweet_id = db.Column('tweet_id', db.Integer, nullable=False)
    option_index = db.Column('option_index', db.Integer, nullable=False)
    intended_hits = db.Column('intended_hits', db.Integer, nullable=False)
    max_tries = db.Column('max_tries', db.Integer, nullable=False)
    create_datetime = \
        db.Column('create_datetime', db.DateTime(), nullable=False)
    status = db.Column('status', db.String(), nullable=False)

    def update_status(self, status: str):
        """
        Update status.

        :param str status: New status.
        """
        self.status = status
        db.session.commit()
