from app import db
from models.vote import Vote

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

    # Columns.
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

    def get_basic_info(self) -> dict:
        """
        Get the information of this model.

        :returns: A dictionary representation of this model.
        """
        return {
            'id': self.id,
            'tweet_id': self.tweet_id,
            'option_index': self.option_index,
            'intended_hits': self.intended_hits,
            'max_tries': self.max_tries,
            'create_datetime':
                self.create_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            'status': self.status
        }

    def get_info(self) -> dict:
        """
        Get the information from this model plus the its vote results.

        :returns: A dictionary that contains all the information. Please refer
            to the `/api/vote-pool-info` API endpoint section in the app README
            for more information.
        """
        info = self.get_basic_info()
        # Count total tries.
        tries = Vote.query.filter(Vote.vote_pool_id == self.id).count()
        # Count hits.
        hits = Vote.query.\
            filter(Vote.vote_pool_id == self.id).\
            filter(Vote.hit == True).count()
        # Build error messages.
        error_votes = Vote.query.\
            filter(Vote.vote_pool_id == self.id).\
            filter(Vote.hit == False).all()
        errors = []
        for vote in error_votes:
            error = {'screen_name': vote.screen_name, 'error': vote.error}
            errors.append(error)
        # Add extra info.
        info['tries'] = tries
        info['hits'] = hits
        info['errors'] = errors
        # Send info.
        return info
