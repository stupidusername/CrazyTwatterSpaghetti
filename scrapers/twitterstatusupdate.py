from lxml import html
from models.account import Account
from scrapers.exceptions \
    import TwitterScrapingException, TwitterStatusUpdateException
from scrapers.twitter import Twitter
from scrapers.twitterlogin import TwitterLogin


class TwitterStatusUpdate(Twitter):
    """
    This class can be used to post a new status on a Twitter account.

    :param TwitterLogin twitter_login: Make the requests as a logged user.
    :param str status: The new status.
    """

    STATUS_CREATE_URL = Twitter.BASE_URL + '/i/tweet/create'

    def __init__(self, twitter_login: TwitterLogin, status: str):
        # Login session.
        session = twitter_login.get_session()
        # Check that the accout is logged in.
        account = twitter_login.get_account()
        if account.status != Account.STATUS_LOGGED_IN:
            raise TwitterStatusUpdateException(
                'Cannot vote. Account status: ' + account.status + '.'
            )
        # Get form authenticity token.
        response = self.make_request(
            session,
            self.BASE_URL,
            'get',
            # If this header is not sent, the user is redirected to an empty
            # page that contains a javascript redirect to the requested page.
            headers={'Referer': self.BASE_URL}
        )
        tree = html.fromstring(response.content)
        elements = tree.xpath("//input[@name='authenticity_token']")
        if not elements:
            raise TwitterScrapingException('Authenticity token not found.')
        authenticity_token = elements[0].get('value')
        if not authenticity_token:
            raise TwitterScrapingException('Authenticity token is empty.')
        # Submit password change.
        data = {
            'authenticity_token': authenticity_token,
            'status': status,
        }
        response = self.make_request(
            session,
            self.STATUS_CREATE_URL,
            'post',
            data=data,
            # The request will not work withouth a proper referer.
            headers={'Referer': self.BASE_URL}
        )
        # Check the result.
        if response.status_code != 200:
            raise TwitterStatusUpdateException(
                'There was an error during the new status update.'
            )
