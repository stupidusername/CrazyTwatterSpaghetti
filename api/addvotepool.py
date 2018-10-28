from app import db
from datetime import datetime
from flask_restful import Resource
from models.votepool import VotePool


class AddVotePool(Resource):
    """
    Flask-RESTful resource.
    """

    def get(
        self,
        tweet_id: int,
        option_index: int,
        intended_hits: int,
        max_tries: int
    ) -> dict:
        """
        Create a vote pool.

        :param int tweet_id: Tweet ID.
        :param int option_index: Option index.
        :param int intended_hits: Intended number of votes.
        :param int max_tries: Maximum numer of tries.
        :returns: A dictionary representation of a `VotePool` instance.
        """
        vote_pool = VotePool(
            tweet_id=tweet_id,
            option_index=option_index,
            intended_hits=intended_hits,
            max_tries=max_tries,
            create_datetime=datetime.utcnow(),
            status=VotePool.STATUS_RUNNING
        )
        db.session.add(vote_pool)
        db.session.commit()
        return vote_pool.get_basic_info()
