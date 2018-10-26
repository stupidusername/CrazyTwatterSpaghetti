from lxml import html
import re
from scrapers.exceptions import TwitterScrapingException, TwitterVoteException
from scrapers.twitterlogin import TwitterLogin
from scrapers.twitterstatus import TwitterStatus
from typing import List, Optional


class TwitterPoll(TwitterStatus):
    """
    This class represents a twitter poll and it uses scraping to get its
    information.

    :param int id: Tweet id.
    :param None|TwitterLogin twitter_login: Make the requests as a logged user.
    """

    def __init__(self, id: int, twitter_login: Optional[TwitterLogin] = None):
        # Get session to pass to the parent constructor.
        session = twitter_login.get_session if twitter_login else None
        super(TwitterPoll, self).__init__(id, session)
        # Default attribute values.
        self._twitter_login = twitter_login
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
                response = self._session.get(self._poll_url, headers=headers)
                poll_tree = html.fromstring(response.content)
                # Check the status of the poll.
                elements = poll_tree.find_class('PollXChoice')
                if elements:
                    poll_status = elements[0].get('data-poll-init-state')
                    if poll_status == 'opened':
                        self._finished = False
                    elif poll_status == 'final':
                        self._finished = True
                if self._finished is None:
                    # Raise an exception if the poll status was not determined.
                    raise TwitterScrapingException(
                        'Poll status could not be determined.'
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
                # Get options
                elements = poll_tree.find_class('PollXChoice-choice--text')
                for element in elements:
                    try:
                        index = int(element.get('data-poll-index'))
                    except TypeError:
                        raise TwitterScrapingException(
                            'Option index could not be determined.'
                        )
                    children = element.getchildren()
                    if len(children) < 2:
                        raise TwitterScrapingException(
                            'Option value could not be determined.'
                        )
                    value = children[1].text_content()
                    percentage_text = children[0].text[:-1]  # Remove "%".
                    try:
                        percentage = int(percentage_text)
                    except TypeError:
                        raise TwitterScrapingException(
                            'Option votes could not be determined.'
                        )
                    votes = int(round(self._total_votes * percentage / 100))
                    self._options.append({
                        'index': index,
                        'value': value,
                        'votes': votes
                    })
                if not self._options:
                    # Options could not be determined. Raise an exception.
                    raise TwitterScrapingException(
                        'Options could not be determined.'
                    )

    def is_poll(self) -> Optional[bool]:
        """
        Check if the status is a poll.

        :returns: True if the status is a poll. False if the status is not a
            poll. None if the status could not be retrieved.
        """
        return self._is_poll

    def is_finished(self) -> Optional[bool]:
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
            Note: The number of votes of each option is not completely precise.
        """
        return self._options

    def get_total_votes(self) -> Optional[int]:
        """
        Get the total number of votes.

        :returns: The total number of votes or None if the status could not be
            retrieved.
        """
        return self._total_votes

    def vote(self, option_index):
        """
        Vote the specified option.

        :param int option_index: Poll option index (starting from 1).
        """
        if not self._twitter_login:
            raise TwitterVoteException('No account was provided.')
