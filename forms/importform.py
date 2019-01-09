import _thread
from createapp import create_app, db
from csv import DictReader
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
import io
import logging
from logging.handlers import RotatingFileHandler
from models.account import Account
import random
from scrapers.twitterlogin import TwitterLogin
from scrapers.twitterpasswordupdate import TwitterPasswordUpdate
from sqlalchemy import or_
import string
from typing import List
from wtforms import BooleanField


class ImportForm(FlaskForm):
    """
    CSV import form class.
    """

    file = FileField('File', validators=[
        FileRequired(),
        FileAllowed(['csv'])
    ])
    change_passwords = BooleanField('Change Passwords')

    def save(self):
        """
        Save the accounts imported from the CSV file.
        """
        if self.file.data:
            stream = io.StringIO(
                self.file.data.read().decode("UTF8"),
                newline=None
            )
            reader = DictReader(
                stream,
                fieldnames=(
                    'screen_name',
                    'email',
                    'password',
                    'phone_number',
                    'proxy'
                )
            )
            # Avoid accounts that were already loaded.
            rows = []
            for row in reader:
                account = Account.query.filter(
                    or_(
                        Account.screen_name == row['screen_name'],
                        Account.email == row['screen_name']
                    )
                ).first()
                if not account:
                    rows.append(row)
            if self.change_passwords.data:
                # Change passwords if needed.
                _thread.start_new_thread(self._change_passwords, (rows,))
            else:
                # Save the accounts otherwise.
                db.session.bulk_save_objects(
                    [Account(**row) for row in rows]
                )
                db.session.commit()
        else:
            raise Exception(
                'The uploaded file is an empty instance of FileStorage.'
            )

    def _change_passwords(self, rows: List[dict]):
        """
        Change the password of the accounts that are loaded in the `dict`
        param. Also save the accounts to the DB.

        :param [dict] rows: A list containing the information of the accounts.
        """
        # Push an app context.
        app = create_app()
        app.app_context().push()
        # Create a rotating log for errors.
        logger = logging.getLogger()
        logger.setLevel(logging.ERROR)
        handler = RotatingFileHandler(
            'logs/password_update.log',
            maxBytes=65536,
            backupCount=5
        )
        logger.addHandler(handler)
        # Also send errors to stderr.
        logger.addHandler(logging.lastResort)
        # Each row represents the information of one account.
        for row in rows:
            # Create the account model.
            account = Account(**row)
            # Generate the new password.
            chars = string.ascii_letters + string.digits
            new_password = ''.join((random.choice(chars)) for x in range(8))
            try:
                # Update the account password.
                TwitterPasswordUpdate(TwitterLogin(account), new_password)
                # Save the new password.
                account.password = new_password
            except Exception as e:
                # There was an error during the password update.
                logger.error(
                    '"%s" password update failed with exception: %s',
                    account.screen_name,
                    e
                )
            # Save the account to the DB.
            db.session.add(account)
            db.session.commit()
