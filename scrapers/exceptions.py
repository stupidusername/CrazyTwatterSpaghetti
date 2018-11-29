class TwitterScrapingException(Exception):
    """
    An exception raised when an error occurs during scraping.
    """
    pass


class TwitterLoginException(TwitterScrapingException):
    """
    An exception raised during a login.
    """
    pass


class TwitterVoteException(TwitterScrapingException):
    """
    An exception raised during a poll vote.
    """
    pass


class TwitterPasswordUpdateException(TwitterScrapingException):
    """
    An exception raised during a password update.
    """
    pass
