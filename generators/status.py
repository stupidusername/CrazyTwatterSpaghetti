from generators.exceptions import GeneratorException
import json
import requests


def get_random() -> str:
    """
    Get a random quote ready to be used as a Twitter status.

    :returns: A random string.
    :raises GeneratorException:
    """
    try:
        r = requests.get('http://quotes.stormconsultancy.co.uk/random.json')
        jo = json.loads(r.content)
        return jo['quote']
    except Exception as e:
        raise GeneratorException('Failed to get random status: ' + str(e))
