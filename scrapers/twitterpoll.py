from twitterstatus import TwitterStatus
from typing import List, Union


class TwitterPoll(TwitterStatus):
    """
    This class represents a twitter poll and it uses scraping to get its
    information.

    :param int id: Tweet id.
    """

    def __init__(self, id):
        super(TwitterPoll, self).__init__(id)
        # Default attribute values.
        self._is_poll = None
        self._finished = None
        self._options = []
        self._total_votes = None
        # Populate attributes.
        if self._tree is not None:
            # TODO: Populate attributes
            pass

    def is_poll(self) -> Union[bool, None]:
        """
        Check if the status is a poll.

        :returns: True if the status is a poll. False if the status is not a
            poll. None if the status could not be retrieved.
        """
        return self._is_poll

    def is_finished(self) -> Union[bool, None]:
        """
        Check if the poll is finished.

        :returns: True if the poll is finished. False if the poll is not
            finished. None if the status could not be retrieved.
        """
        return self._is_finished

    def get_options(self) -> List[dict]:
        """
        Get the answer options.

        :returns: A list of dictionaries with the following format:
            ```
            [
                {
                    'index': int,
                    'value': str,
                    'votes': int | None
                }
            ]
            ```
            Note: The number of votes of each option will take the value `None`
                if it cannot be determined.
        """
        return self._options

    def get_total_votes(self) -> Union[int, None]:
        """
        Get the total number of votes.

        :returns: The total number of votes or None if the status could not be
            retrieved.
        """
        return self._total_votes
