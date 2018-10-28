from app import running_vote_pool_ids
from flask_restful import Resource
from models.votepool import VotePool
from scrapers.twitterpoll import TwitterPoll


class VotePoolInfo(Resource):
    """
    Flask-RESTful resource.
    """

    def get(self, id: int) -> dict:
        """
        Get information from a vote pool.

        :param int id: Vote pool ID.
        :returns:
        """
        vote_pool = VotePool.query.filter(VotePool.id == id).first()
        # If the pool is not finished and is not listed as a current running
        # pool change its status to interrupted.
        finished = vote_pool.status == VotePool.STATUS_FINISHED
        if not finished and vote_pool.id not in running_vote_pool_ids:
            vote_pool.update_status(VotePool.STATUS_INTERRUPTED)
        return vote_pool.get_info()
