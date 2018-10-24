from lxml import html
import re
from scrapers.exceptions import TwitterScrapingException
from scrapers.twitterstatus import TwitterStatus
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
        # Poll iframe URL.
        self._poll_url = None
        # Populate attributes if the status was retrieved.
        if self._status:
            elements = \
                self._tree.xpath("//div[contains(@class, 'card-type-poll')]")
            if elements:
                self._is_poll = True
                # Build tree element for the poll iframe. The referer must be
                # sent in the headers of the request to avoid a 403 status.
                self._poll_url = self.BASE_URL + elements[0].get('data-src')
                headers = {'Referer': self._status_url}
                r = self._session.get(self._poll_url, headers=headers)
                poll_tree = html.fromstring(r.content)
                # Check the state of the poll.
                elements = poll_tree.find_class('PollXChoice')
                if elements:
                    state = elements[0].get('data-poll-init-state')
                    if state == 'final':
                        self._finished = True
                    elif state == 'opened':
                        self._finished = False
                if self._finished is None:
                    # Raise an exception if the state could not be determined.
                    raise TwitterScrapingException(
                        'Poll state could not be determined.'
                    )
                # Get the total number of votes.
                elements = poll_tree.find_class('PollXChoice-footer--total')
                if elements:
                    text = elements[0].text
                    numbers = re.findall('\d+', text)
                    if numbers:
                        self._total_votes = int(''.join(numbers))
                if self._total_votes is None:
                    # Total votes could not be determined. Raise an exception.
                    raise TwitterScrapingException(
                        'Total votes could not be determined.'
                    )


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
        return self._finished

    def get_options(self) -> List[dict]:
        """
        Get the answer options.

        :returns: A list of dictionaries with the following format:
            ```
            [
                {
                    'index': int,
                    'value': str,
                    'votes': int
                }
            ]
            ```
        """
        return self._options

    def get_total_votes(self) -> Union[int, None]:
        """
        Get the total number of votes.

        :returns: The total number of votes or None if the status could not be
            retrieved.
        """
        return self._total_votes
