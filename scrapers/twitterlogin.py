from lxml import html
from models.account import Account
import requests
from scrapers.exceptions import TwitterScrapingException
from scrapers.twitter import Twitter


class TwitterLogin(Twitter):
    """
    This scraper can be used to login a Twitter account.

    :const str LOGIN_URL: Login URL.
    :const str SESSIONS_URL: Sessions URL (used for login form submission).
    :param Account account: Account model instance.
    """

    LOGIN_URL = Twitter.BASE_URL + '/login'
    SESSIONS_URL = Twitter.BASE_URL + '/sessions'

    def __init__(self, account: Account):
        # Session used to keep cookies.
        self._session = requests.Session()
        # Default attribute values
        self._account = account
        # Store cookies because they are cleaned later on.
        self._cookies = self._account.cookies
        # Set the account status to undetermined beforehand in case any error
        # occurs.
        self._account.update_status(Account.STATUS_UNDETERMINED)
        # Cookies will only be saved after a successful login.
        # Reset them for now.
        self._account.set_cookies(None)
        # Create the element tree.
        response = self.make_request(self._session, self.LOGIN_URL, 'get')
        tree = html.fromstring(response.content)
        # Check for the existence of the login form.
        if len(tree.forms) < 3:
            # Login form not found. Raise Exception.
            raise TwitterScrapingException('Login form not found.')
        # Complete form fields.
        form = tree.forms[2]
        fields = form.fields
        try:
            fields['session[username_or_email]'] = self._account.screen_name
            fields['session[password]'] = self._account.password
        except KeyError:
            raise TwitterScrapingException('Login form could not be filled.')
        # Submit the form.
        response = self.make_request(
            self._session,
            self.SESSIONS_URL,
            'post',
            data=dict(form.form_values())
        )
        print(response.text)
