from lxml import html
import requests
from typing import Union


class TwitterStatus(object):
    """
    This class represents a twitter status and it uses scraping to get its
    information.

    :param int id: Tweet id.
    """

    def __init__(self, id: int):
        self._id = id
        self._status = None
        page = requests.get('https://twitter.com/statuses/' + str(self._id))
        self._tree = html.fromstring(page.content)

    def get_status(self) -> Union[str, None]:
        """
        Get the status message.

        :returns: The status message or None if the status could not be
            retrieved.
        """
        if not self._status:
            elements = self._tree.find_class('TweetTextSize--jumbo')
            self._status = elements[0].text if elements else None
        return self._status
