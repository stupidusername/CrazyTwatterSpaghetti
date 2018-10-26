from lxml import html
from models.account import Account
import pickle
import requests
from requests import Response
from scrapers.exceptions import TwitterScrapingException
from scrapers.twitter import Twitter
from urllib import parse


class TwitterLogin(Twitter):
    """
    This scraper can be used to login a Twitter account.

    :const str LOGIN_URL: Login URL.
    :const str LOGIN_URL: Login URL.
    :const str SESSIONS_URL: Sessions URL (used for login form submission).
    :const str CHALLENGE_URL: Login challenge URL.
    :param Account account: Account model instance.
    """

    LOGIN_URL = Twitter.BASE_URL + '/login'
    LOGIN_ERROR_URL = Twitter.BASE_URL + '/login/error'
    SESSIONS_URL = Twitter.BASE_URL + '/sessions'
    CONFIRM_ACCESS = Twitter.BASE_URL + '/account/access'
    CHALLENGE_URL = Twitter.BASE_URL + '/account/login_challenge'

    def __init__(self, account: Account):
        # Session used to keep cookies.
        self._session = requests.Session()
        # Default attribute values.
        self._account = account
        # Store cookies because they are cleaned later on.
        self._cookies = self._account.cookies
        # Set the account status to undetermined beforehand in case any error
        # occurs.
        self._account.update_status(Account.STATUS_UNDETERMINED)
        # Cookies will only be saved after a successful login.
        # Reset them for now.
        self._account.set_cookies(None)
        # Begin the login process.
        self._login()

    def _login(self):
        """
        Try to login.
        """
        # Restore cookies if any.
        if self._cookies:
            self._session.cookies.update(pickle.loads(self._cookies))
        # Get the login page.
        response = self.make_request(self._session, self.LOGIN_URL, 'get')
        # Create the element tree.
        tree = html.fromstring(response.content)
        # Check for login redirect. This occurs if the cookies are valid.
        scripts = tree.xpath('//script')
        if scripts:
            redirect = 'location.replace(location.href.split("#")[0]);'
            if redirect in scripts[0].text_content():
                # Redirect found. Check if there is any challenge to solve and
                # determine the status.
                self._check_for_challenge(response)
                self._determine_status(response)
                return
        # Cookies were not set or they did not work.
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
        # Check if there is any challenge to solve and determine the status.
        self._check_for_challenge(response)
        self._determine_status(response)

    def _check_for_challenge(self, response: Response):
        """
        Check if the response of the login was redirected to the challenge
        page and try to solve it.

        :param Response response: Response got from the login attempt.
        """
        # Check if the response URL matches the challenge URL.
        if response.url.startswith(self.CHALLENGE_URL):
            # Try to solve the challenge.
            tree = html.fromstring(response.content)
            if tree.forms:
                # Check if Twitter is asking for an email or a phone number.
                challenge = None
                # Get URL query params.
                q_params = dict(
                    parse.parse_qsl(parse.urlsplit(response.url).query)
                )
                if 'challenge_type' in q_params:
                    q_param = q_params['challenge_type']
                    if q_param == 'RetypeEmail':
                        challenge = 'email'
                    elif q_param == 'RetypePhoneNumber':
                        challenge = 'phone_number'
                if not challenge:
                    # The challenge type could not be determined.
                    raise TwitterScrapingException(
                        'Challenge type could not be determined.'
                    )
                # Complete the form.
                form = tree.forms[0]
                fields = form.fields
                try:
                    value = {
                        'email': self._account.email,
                        'phone_number': self._account.phone_number
                    }[challenge]
                    fields['challenge_response'] = value
                except KeyError:
                    raise TwitterScrapingException('')
                # Submit the form.
                response = self.make_request(
                    self._session,
                    self.SESSIONS_URL,
                    'post',
                    data=dict(form.form_values())
                )
            else:
                raise TwitterScrapingException('Challenge form not found.')

    def _determine_status(self, response: Response):
        """
        Determine and save the account status. Save the cookies in the case
        that the login process was successful.

        :param Response response: Response got from the login attempt.
        """
        # The login is redirected to an error page if the supplied account
        # credentials are wrong.
        if response.url.startswith(self.LOGIN_ERROR_URL):
            self._account.update_status(Account.STATUS_WRONG_CREDENTIALS)
            return
        # Make a request to the home page to check the status.
        home_response = self.make_request(self._session, self.BASE_URL, 'get')
        # If the request was redirected to an account access check we can not
        # continue.
        if home_response.url.startswith(self.CONFIRM_ACCESS):
            self._account.update_status(Account.STATUS_UNCONFIRMED_ACCESS)
            return
        self._account.set_cookies(pickle.dumps(self._session.cookies))
