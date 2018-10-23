from flask_restful import Resource


class PollVote(Resource):
    """
    Flask-RESTful resource.
    """

    def get(self, tweet_id: int, option_index: int, votes: int) -> dict:
        """
        Use the loaded accounts to try to give a certain number of votes to a
        given poll option.

        :param int tweet_id: Tweet ID.
        :param int option_index: Option index.
        :param int votes: Intended number of votes.
        :returns: A dictionary with the following format:
            ```
            {
                'tries': int,
                'hits': int,
                'errors': [
                    {
                        'screen_name': str,
                        'error': str
                    }
                ]
            }
            ```
        """
        return {
            'tries': 0,
            'hits': 0,
            'errors': []
        }
