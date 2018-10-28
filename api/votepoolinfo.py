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
        return vote_pool.get_basic_info()
