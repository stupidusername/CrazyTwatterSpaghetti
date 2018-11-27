# CrazyTwatterSpaghetti


## Requirements

- Python >= 3.6 (Tested on 3.6.6).
- Pip packages listed on `requirements.txt`.
- A RDBMS supported by SQLAlchemy. See [SQLAlchemy 1.2 Documentation > Dialects](https://docs.sqlalchemy.org/en/latest/dialects/index.html).


## Installation

- Create a `config.ini`. Change the database DSN and the secret key used for cookies. Use `config-example.ini` as reference.
- Apply DB migrations: `$ alembic upgrade head`.


## Usage

Run the flask application defined in `app.py`. See [Flask deployment options](http://flask.pocoo.org/docs/1.0/deploying/).

Note: Dates and times are displayed in UTC.


## Using proxies

An optional proxy can be specified for each account.


## Accounts CSV format

`<screen_name>,<email>,<password>,<phone_number>,<proxy_url>`


## API endpoints

- `/api/poll-info/<tweet_id>`

  Get information about a twitter poll given its tweet id.

  - Response example if the tweet is a poll:

    ```
    {
      "poll": true,
      "finished": false,
      "status": "What is your favorite type of pasta?",
      "options": [
        {
          "index": 1,
          "value": "Ravioli",
          "votes": 7
        },
        {
          "index": 2,
          "value": "Macaroni",
          "votes": 15
        },
        {
          "index": 3,
          "value": "Code Spaghetti",
          "votes": 63
        }
      ],
      "total_votes": 85
    }
    ```

    Note: The number of votes of each option is not completely precise.

  - Response example for other types of tweets:

    ```
    {
      "poll": false,
      "finished": null,
      "status": null,
      "options": [],
      "total_votes": null
    }
    ```

  - Response example for non-accessible tweets:

    ```
    {
      "poll": None,
      "finished": null,
      "status": null,
      "options": [],
      "total_votes": null
    }
    ```

- `/api/add-vote-pool/<tweet_id>/<option_index>/<intended_hits>/<max_tries>`

  Start a vote pool. This method responds as soon as the pool is created.
  The status of the pool can be checked later on.

  - Params:

    - `tweet_id`: Twitter status id.
    - `option_index`: Selected option index.
    - `intended_hits`: Intended number of successful votes.
    - `max_tries`: Maximum number of tries.

  - Response example:

    ```
    {
      "id": 1,
      "tweet_id": 1111111111111111111,
      "option_index": 1,
      "intended_hits": 10,
      "max_tries": 100,
      "create_datetime": "2018-10-21 23:38:51",
      "status": "running"
    }
    ```

- `/api/vote-pool-info/<id>`

  Check the status of the vote pool give its id.

  - Response example:

    ```
    {
      "id": 1,
      "tweet_id": 1111111111111111111,
      "option_index": 1,
      "intended_hits": 10,
      "max_tries": 100,
      "create_datetime": "2018-10-21 23:38:51",
      "status": "finished",
      "tries": 11,
      "hits": 10,
      "errors": [
        {
          "screen_name": "john_doe",
          "error": "Cannot vote. Account status: suspended."
        }
      ]
    }
    ```

  - Notes:

    - `status` can take the values `running`, `finished` or `interrupted`.
    - The number of tries can be lower than the specified if there are no enough available accounts.
