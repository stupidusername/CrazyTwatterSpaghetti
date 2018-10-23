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
- `api/poll-info/<tweet_id>`

  Get information about a twitter poll given its tweet id.

  Response example if the tweet is a poll:
  ```
  {
    "poll": true,
    "finished": false,
    "question": "What is your favorite type of pasta?",
    "options": [
      {
        "value": "Ravioli",
        "votes": 7
      },
      {
        "value": "Macaroni",
        "votes": 15
      },
      {
        "value": "Code Spaghetti",
        "votes": 63
      }
    ]
  }
  ```

  Response example for other types of tweets:

  ```
  {
    "poll": false,
    "finished": null,
    "question": null,
    "options": []
  }
  ```
