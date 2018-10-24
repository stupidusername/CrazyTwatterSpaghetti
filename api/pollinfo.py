from flask_restful import Resource


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
        return {
            'poll': False,
            'finished': None,
            'status': None,
            'options': [],
            'total_votes': None
        }
