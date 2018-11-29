import json
from lxml import html
from models.account import Account
import re
from scrapers.exceptions import TwitterScrapingException, TwitterVoteException
from scrapers.twitterlogin import TwitterLogin
from scrapers.twitterstatus import TwitterStatus
from typing import List, Optional
from urllib import parse


class TwitterPoll(TwitterStatus):
    """
    This class represents a twitter poll and it uses scraping to get its
    information.

    :const str VOTE_URL: Vote submission URL.
    :param int id: Tweet id.
    :param None|TwitterLogin twitter_login: Make the requests as a logged user.
    """

    VOTE_URL = 'https://caps.twitter.com/v2/capi/passthrough/1'

    def __init__(self, id: int, twitter_login: Optional[TwitterLogin] = None):
        # Get session and pass it to the parent constructor.
        session = twitter_login.get_session() if twitter_login else None
        super(TwitterPoll, self).__init__(id, session)
        # Default attribute values.
        self._twitter_login = twitter_login
        self._is_poll = None
        self._finished = None
        self._options = []
        self._total_votes = None
        # Poll iframe URL.
        self._poll_url = None
        # Poll element tree.
        self._poll_tree = None
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
                response = self.make_request(
                    self._session,
                    self._poll_url,
                    'get',
                    headers=headers
                )
                self._poll_tree = html.fromstring(response.content)
                # Check the status of the poll.
                elements = self._poll_tree.find_class('PollXChoice')
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
                elements = \
                    self._poll_tree.find_class('PollXChoice-footer--total')
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
                elements = \
                    self._poll_tree.find_class('PollXChoice-choice--text')
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
        # Check that the twitter status is a poll.
        if not self.is_poll():
            raise TwitterVoteException('The provided status is not a poll.')
        # Check that the poll is not finished.
        if self.is_finished():
            raise TwitterVoteException('The poll is finished.')
        # Check that option index is valid.
        if 1 > option_index or option_index > len(self.get_options()):
            raise TwitterVoteException('Option index not valid.')
        # Check that an account was provided.
        if not self._twitter_login:
            raise TwitterVoteException('No account was provided.')
        # Check that the accout is logged in.
        account = self._twitter_login.get_account()
        if account.status != Account.STATUS_LOGGED_IN:
            raise TwitterVoteException(
                'Cannot vote. Account status: ' + account.status + '.'
            )
        # Proceed to try to vote.
        # First will try to figure if the user already voted.
        # Get the parameters to make the vote request.
        # The parameters we are looking for are outside the iframe.
        # Search the status tree.
        divs = self._tree.xpath(
            "//div["
            "contains(@class, 'js-macaw-cards-iframe-container') and"
            "contains(@data-card-url, 'card://')"
            "]"
        )
        if not divs:
            # Poll iframe container not found.
            raise TwitterScrapingException('Poll iframe container not found.')
        # Get parameters from the container.
        container = divs[0]
        card_uri = container.get('data-card-url')
        card_name = container.get('data-card-name')
        if not card_uri or not card_name:
            # Some parameter was not found.
            raise TwitterScrapingException('Vote request parameter not found.')
        # Create request parameters.
        data = {
            'twitter:long:original_tweet_id': self._id,
            'twitter:string:card_uri': card_uri,
            'twitter:string:cards_platform': 'Web-12',  # Assumed as constant.
            'twitter:string:response_card_name': card_name
        }
        # Get the bearer token from the init script.
        links = self._tree.xpath(
            "//link[contains(@href, '/init.')]"
        )
        if not links:
            # Script not found.
            raise TwitterScrapingException('Status init script not found.')
        # Get script link.
        link = links[0].get('href')
        # Get the script. No need for use a session.
        script_response = self.make_request(None, link, 'get')
        # Extract the bearer token from the script.
        js = script_response.text
        try:
            bearer_token = \
                re.search('t\.a="([^"]*)"', js).group(1)
        except AttributeError:
            # Bearer token not found.
            raise TwitterScrapingException('Poll bearer token not found.')
        try:
            auth_token = self._session.cookies['ct0']
        except KeyError:
            # Auth token not found.
            raise TwitterScrapingException('Vote auth token not found.')
        # Create headers.
        headers = {
            'Authorization': 'Bearer ' + bearer_token,
            'X-Csrf-Token': auth_token,
            'X-Twitter-Auth-Type': 'OAuth2Session',
        }
        # Make the request. Important: This must be a GET request.
        vote_reponse = self.make_request(
            self._session,
            self.VOTE_URL,
            'get',
            params=data,
            headers=headers
        )
        # Check for a response error.
        if vote_reponse.status_code != 200:
            raise TwitterVoteException('Error during vote check.')
        # Now check the reponse and try to find a selected choice.
        try:
            parsed = json.loads(vote_reponse.text)
        except ValueError:
            raise TwitterScrapingException('Vote reponse could not be parsed.')
        try:
            selected_choice = \
                parsed['card']['binding_values']['selected_choice']
            if selected_choice:
                # We found a previously selected choice.
                raise TwitterVoteException('The account already voted.')
        except KeyError:
            # No previously selected choice was found.
            pass
        # Do the actual vote request.
        # Add the selected option to the request parameters.
        data['twitter:string:selected_choice'] = option_index
        # Make the request.
        vote_reponse = self.make_request(
            self._session,
            self.VOTE_URL,
            'post',
            data=data,
            headers=headers
        )
        # Check for a response error.
        if vote_reponse.status_code != 200:
            raise TwitterVoteException('Error during vote request.')
