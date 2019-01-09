from lxml import html
from models.account import Account
from scrapers.exceptions \
    import TwitterScrapingException, TwitterPasswordUpdateException
from scrapers.twitter import Twitter
from scrapers.twitterlogin import TwitterLogin


class TwitterPasswordUpdate(Twitter):
    """
    This class can be used to change the password of a Twitter account.

    :param TwitterLogin twitter_login: Make the requests as a logged user.
    :param str new_password:
    """

    PASSWORD_SETTINGS_URL = Twitter.BASE_URL + '/settings/password'
    PASSWORD_UPDATE_URL = Twitter.BASE_URL + '/settings/passwords/update'
    PASSWORD_RESET_CONFIRMATION_URL = \
        Twitter.BASE_URL + '/settings/passwords/password_reset_confirmation'

    def __init__(self, twitter_login: TwitterLogin, new_password: str):
        # Check if the account is logged in.
        if twitter_login.get_account().status != Account.STATUS_LOGGED_IN:
            raise TwitterPasswordUpdateException(
                'The account is not logged in.'
            )
        # Login session.
        session = twitter_login.get_session()
        # Current password of the account.
        current_password = twitter_login.get_account().password
        # Get form authenticity token.
        response = self.make_request(
            session,
            self.PASSWORD_SETTINGS_URL,
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
            '_method': 'PUT',
            'authenticity_token': authenticity_token,
            'current_password': current_password,
            'user_password': new_password,
            'user_password_confirmation': new_password
        }
        response = self.make_request(
            session,
            self.PASSWORD_UPDATE_URL,
            'post',
            data=data,
            # The request will not work withouth a proper referer.
            headers={'Referer': self.PASSWORD_SETTINGS_URL}
        )
        # Check the result
        if not response.url.startswith(self.PASSWORD_RESET_CONFIRMATION_URL):
            raise TwitterPasswordUpdateException(
                'There was an error during password update.'
            )
