import _thread
from createapp import create_app, db, running_vote_pool_ids
from datetime import datetime
from flask_restful import Resource
from models.account import Account
from models.vote import Vote
from models.votepool import VotePool
from random import random
from scrapers.twitterlogin import TwitterLogin
from scrapers.twitterpoll import TwitterPoll
from sqlalchemy.sql.expression import case
from time import sleep


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
        # Successful votes.
        self._hits = 0
        # Create and save the new vote pool.
        self._vote_pool = VotePool(
            tweet_id=tweet_id,
            option_index=option_index,
            intended_hits=intended_hits,
            max_tries=max_tries,
            create_datetime=datetime.utcnow(),
            status=VotePool.STATUS_RUNNING
        )
        db.session.add(self._vote_pool)
        db.session.commit()
        # Start the vote requests in a new thread.
        _thread.start_new_thread(self._vote, (self._vote_pool.id,))
        # Return the vote pool information.
        return self._vote_pool.get_basic_info()

    def _vote(self, vote_pool_id: int):
        """
        Make the vote requests.

        :param int vote_pool_id: Vote pool ID.
        """
        # Push an app context.
        app = create_app()
        app.app_context().push()
        # We need to create the model again because the same db session cannot
        # be used from two different threads.
        vote_pool = VotePool.query.filter(VotePool.id == vote_pool_id).first()
        # Add this pool to the list of running vote pools.
        running_vote_pool_ids.append(vote_pool.id)
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
            limit(vote_pool.max_tries).all()
        # Try while there are available accounts and the intended hits was not
        # reached.
        while accounts and self._hits < vote_pool.intended_hits:
            # Sleep for a random amount of time if the previos try was a hit.
            # Error could be undeclared.
            if 'error' in locals() and not locals()['error']:
                sleep(random() * 60)  # Sleep for a maximum of one minute.
            account = accounts.pop(0)
            error = None
            # Try to vote.
            try:
                twitter_login = TwitterLogin(account)
                twitter_poll = \
                    TwitterPoll(vote_pool.tweet_id, twitter_login)
                twitter_poll.vote(vote_pool.option_index)
            except Exception as e:
                error = str(e)
            # Save the result.
            vote = Vote(
                vote_pool_id=vote_pool.id,
                create_datetime=datetime.utcnow(),
                screen_name=account.screen_name,
                email=account.email,
                password=account.password,
                phone_number=account.phone_number,
                hit=not error,
                error=error
            )
            db.session.add(vote)
            db.session.commit()
            if not error:
                self._hits += 1
        # The vote pool has finished. Update its status.
        vote_pool.update_status(VotePool.STATUS_FINISHED)
        # Remove it from the list of running vote pools.
        running_vote_pool_ids.remove(vote_pool.id)
