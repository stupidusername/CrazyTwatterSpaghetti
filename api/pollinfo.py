from flask_restful import Resource
from scrapers.twitterpoll import TwitterPoll


class PollInfo(Resource):
    """
    Flask-RESTful resource.
    """

    def get(self, tweet_id: int) -> dict:
        """
        Get information from a poll.

        :param int tweet_id: Tweet ID.
        :returns: A dictionary with the following format:
            ```
            {
                'poll': bool | None,
                'finished': bool | None,
                'status': None | str,
                'options': [
                    {
                        'index': int,
                        'value': str,
                        'votes': int
                    }
                ],
                'total_votes': int | None
            }
            ```
        """
        poll = TwitterPoll(tweet_id)
        return {
            'poll': poll.is_poll(),
            'finished': poll.is_finished(),
            'status': poll.get_status(),
            'options': poll.get_options(),
            'total_votes': poll.get_total_votes()
        }
