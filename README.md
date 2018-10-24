# CrazyTwatterSpaghetti

## Requirements
- Python >= 3.6 (Tested on 3.6.6).
- Pip packages listed on `requirements.txt`.
- A RDBMS supported by SQLAlchemy. See [SQLAlchemy 1.2 Documentation > Dialects](https://docs.sqlalchemy.org/en/latest/dialects/index.html).

## Installation
- Create a `config.ini`. Change the database DSN and the secret key used for cookies. Use `config-example.ini` as reference.
- Apply DB migrations: `$ alembic upgrade head`.

## Usage
Run the flask application defined in `app.py`.

## Accounts CSV format
`<screen_name>, <email>, <password>, <phone_number>`

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

- `/api/poll-vote/<tweet_id>/<option_index>/<votes>`

  Use the loaded accounts to try to give a certain number of votes to a given poll option.
  The number of tries will be lower than the specified number of votes if there is no enough accounts loaded.

  - Response example:

    ```
    {
      "tries": 10,
      "hits": 9,
      "errors": [
        {
          "screen_name": "john_doe",
          "error": "Unable to login: non-existing user or incorrect password."
        }
      ]
    }
    ```
