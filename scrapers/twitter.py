import requests
from requests import Response, Session
from requests.exceptions import RequestException
from scrapers.exceptions import TwitterScrapingException
from typing import Any, Union


class Twitter(object):
    """
    Abastract base class for twitter scrappers.

    :const str BASE_URL: Twitter base URL.
    """

    BASE_URL = 'https://twitter.com'

    @staticmethod
    def make_request(
        session: Union[None, Session],
        url: str,
        method: str,
        **kwargs: Any
    ) -> Response:
        """
        Make a request to an URL.

        :param None | Session sesion: Session to be used for the request.
        :param str url: URL.
        :param str method: `get` or `porst`.
        :param **kwargs: Keyword arguments passed to the request method.
        """
        method = getattr((session if session else requests), method)
        try:
            response = method(url, **kwargs)
            return response
        except RequestException:
            raise TwitterScrapingException('Error during request.')
