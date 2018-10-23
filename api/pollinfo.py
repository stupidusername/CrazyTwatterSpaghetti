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
                'poll': bool,
                'finished': None | bool,
                'question': None | str,
                'options': [
                    {
                        'index': int,
                        'value': str,
                        'votes': int,
                    }
                ]
            }
            ```
        """
        return {
            'poll': False,
            'finished': None,
            'question': None,
            'options': []
        }
