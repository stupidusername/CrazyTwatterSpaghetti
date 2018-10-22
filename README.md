# CrazyTwatterSpaghetti

## Requirements
- Python >= 3.6.
- Pip packages listed on `requirements.txt`.
- A RDBMS supported by SQLAlchemy. See [SQLAlchemy 1.2 Documentation > Dialects](https://docs.sqlalchemy.org/en/latest/dialects/index.html).

## Installation
- Create a `config.ini`. Change the database DSN and the secret key used for cookies. Use `config-example.ini` as reference.
- Apply DB migrations: `$ alembic upgrade head`.

## Usage
Run the flask application defined in `app.py`.

## Accounts CSV format
`<screen_name>, <email>, <password>, <phone_number>`
