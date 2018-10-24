from lxml import html
import requests
from  requests.exceptions import RequestException
from typing import Union


class TwitterStatus(object):
    """
    This class represents a twitter status and it uses scraping to get its
    information.

    :param int id: Tweet id.
    """

    def __init__(self, id: int):
        # Default attribute values.
        self._id = id
        self._status = None
        self._tree = None
        # Create the element tree.
        try:
            page = requests.get('https://twitter.com/statuses/' + str(id))
            self._tree = html.fromstring(page.content)
        except RequestException:
            # Failed request.
            pass
        # Populate status.
        if self._tree is not None:
            elements = self._tree.find_class('TweetTextSize--jumbo')
            if elements:
                self._status = elements[0].text

    def get_status(self) -> Union[None, str]:
        """
        Get the status message.

        :returns: The status message or None if the status could not be
            retrieved.
        """
        return self._status
