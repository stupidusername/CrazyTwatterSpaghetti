from lxml import html
from lxml.etree import tostring
import requests
from  requests.exceptions import RequestException
from typing import Union


class TwitterStatus(object):
    """
    This class represents a twitter status and it uses scraping to get its
    information.

    :const str BASE_URL: Twitter base URL.
    :param int id: Tweet id.
    """

    BASE_URL = 'https://twitter.com'

    def __init__(self, id: int):
        # Session used to keep cookies.
        self._session = requests.Session()
        # Default attribute values.
        self._id = id
        self._status = None
        self._tree = None
        # Status URL.
        self._status_url = self.BASE_URL + '/statuses/' + str(self._id)
        # Create the element tree.
        try:
            r = self._session.get(self._status_url)
            self._tree = html.fromstring(r.content)
        except RequestException:
            # Failed request.
            pass
        # Populate status if the element tree was created.
        if self._tree is not None:
            elements = self._tree.find_class('TweetTextSize--jumbo')
            if elements:
                self._status = elements[0].text_content()

    def get_status(self) -> Union[None, str]:
        """
        Get the status message.

        :returns: The status message or None if the status could not be
            retrieved.
        """
        return self._status
