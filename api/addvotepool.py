from app import db
from datetime import datetime
from flask_restful import Resource
from models.account import Account
from models.vote import Vote
from models.votepool import VotePool
from sqlalchemy.sql.expression import case


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
        # Create and save the new vote pool.
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
        # Get the id of the accounts that already voted on the poll.
        screen_names = []
        duplicated_vote_pools = VotePool.query.\
            filter(VotePool.id != vote_pool.id).\
            filter(VotePool.tweet_id == vote_pool.tweet_id).all()
        if duplicated_vote_pools:
            vote_pool_ids = [vp.id for vp in duplicated_vote_pools]
            votes = Vote.query.\
                filter(Vote.vote_pool_id.in_(vote_pool_ids)).\
                filter(Vote.hit == True).all()
            screen_names = [v.screen_name for v in votes]
        # Get the accounts that are the most likely to make a successful vote.
        # Custom order for status column.
        whens = {
            Account.STATUS_LOGGED_IN: 1,
            None: 2,
            Account.STATUS_UNCONFIRMED_ACCESS: 3,
            Account.STATUS_UNDETERMINED: 4,
            Account.STATUS_WRONG_CREDENTIALS: 5,
            Account.STATUS_SUSPENDED: 6
        }
        status_order = case(value=Account.status, whens=whens)
        accounts = Account.query.\
            filter(Account.screen_name.notin_(screen_names)).\
            order_by(
                status_order,
                Account.status_updated_at.desc(),
                Account.id.desc()
            ).\
            limit(max_tries).all()
        return vote_pool.get_basic_info()
