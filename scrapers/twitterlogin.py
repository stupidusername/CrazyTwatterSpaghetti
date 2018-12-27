from lxml import html
from models.account import Account
import pickle
import requests
from requests import Response, Session
from scrapers.exceptions import TwitterLoginException, TwitterScrapingException
from scrapers.twitter import Twitter
from urllib import parse


class TwitterLogin(Twitter):
    """
    This scraper can be used to login a Twitter account.

    :const str LOGIN_URL: Login URL.
    :const str LOGIN_URL: Login URL.
    :const str SESSIONS_URL: Sessions URL (used for login form submission).
    :const str CHALLENGE_URL: Login challenge URL.
    :const str CONSENT_VIOLATION_URL: Consent violation URL.
    :param Account account: Account model instance.
    """

    LOGIN_URL = Twitter.BASE_URL + '/login'
    LOGIN_ERROR_URL = Twitter.BASE_URL + '/login/error'
    SESSIONS_URL = Twitter.BASE_URL + '/sessions'
    CONFIRM_ACCESS_URL = Twitter.BASE_URL + '/account/access'
    CHALLENGE_URL = Twitter.BASE_URL + '/account/login_challenge'
    CONSENT_VIOLATION_URL = Twitter.BASE_URL + '/i/flow/consent_flow'

    def __init__(self, account: Account):
        # Session used to keep cookies.
        self._session = requests.Session()
        # Set the requests session proxies if they are needed.
        if account.proxy:
            proxies = {'http': account.proxy, 'https': account.proxy}
            self._session.proxies.update(proxies)
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

    def get_session(self) -> Session:
        """
        Get the request session.
        """
        return self._session

    def get_account(self) -> Account:
        """
        Get the account model.
        """
        return self._account

    def _login(self):
        """
        Try to login.
        """
        # Restore cookies if any.
        if self._cookies:
            self._session.cookies.update(pickle.loads(self._cookies))
            # Get the login page.
            response = self.make_request(self._session, self.LOGIN_URL, 'get')
            # Check if there is any challenge to solve and determine status.
            self._check_for_challenge(response)
            self._determine_status(response)
            # Check if the login was successful.
            if self._account.status != Account.STATUS_UNDETERMINED:
                return
        # Cookies were not set or they did not work.
        # Get the login page.
        response = self.make_request(self._session, self.LOGIN_URL, 'get')
        # Create the element tree.
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
        # Check if there is any challenge to solve and determine the status.
        self._check_for_challenge(response)
        self._determine_status(response)
        if self._account.status == Account.STATUS_UNDETERMINED:
            # The status could not be determined.
            raise TwitterScrapingException(
                'Account status could not be determined.'
            )

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
                    response.url,
                    'post',
                    data=dict(form.form_values())
                )
                # Check that the submitted information was correct.
                if response.url.startswith(self.CHALLENGE_URL):
                    # Challege response was incorrect.
                    raise TwitterLoginException(
                        'Incorrect challenge response.'
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
        home_response = self.make_request(
            self._session,
            self.BASE_URL,
            'get',
            # If this header is not sent, the user is redirected to an empty
            # page that contains a javascript redirect to the requested page.
            headers={'Referer': self.AFTER_LOGIN_REFERER}
        )
        # If the request was redirected to an account access check we cannot
        # continue.
        if home_response.url.startswith(self.CONFIRM_ACCESS_URL):
            self._account.update_status(Account.STATUS_UNCONFIRMED_ACCESS)
            return
        # Check if the request was redirected to the consent violation flow.
        if home_response.url.startswith(self.CONSENT_VIOLATION_URL):
            # The account is most likely suspended.
            self._account.update_status(Account.STATUS_SUSPENDED)
            return
        # Check if the page contains the profile menu.
        tree = html.fromstring(home_response.content)
        lis = tree.xpath("//li[@id='user-dropdown']")
        if lis:
            # The account is logged in.
            # Check for a suspended account warning.
            divs = tree.xpath("//div[@id='account-suspended']")
            if divs:
                # The account is suspended.
                self._account.update_status(Account.STATUS_SUSPENDED)
                return
            else:
                # The account is likely to be active.
                self._account.update_status(Account.STATUS_LOGGED_IN)
                # Save the cookies.
                self._account.set_cookies(pickle.dumps(self._session.cookies))
                return
