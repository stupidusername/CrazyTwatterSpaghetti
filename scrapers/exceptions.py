class TwitterScrapingException(Exception):
    """
    An exception raised when an error occurs during scraping.
    """
    pass


class TwitterVoteException(TwitterScrapingException):
    """
    An exception raised during a poll vote.
    """
    pass
