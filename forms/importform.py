from app import db
import csv
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
import io
from models.account import Account

class ImportForm(FlaskForm):
    """
    CSV import form class.
    """

    file = FileField('file', validators=[
        FileRequired(),
        FileAllowed(['csv'])
    ])

    def save(self):
        """
        Save the accounts imported from the CSV file.
        """
        if self.file.data:
            stream = io.StringIO(
                self.file.data.read().decode("UTF8"),
                newline=None
            )
            reader = csv.DictReader(
                stream,
                fieldnames=(
                    'screen_name',
                    'email',
                    'password',
                    'phone_number',
                    'proxy'
                )
            )
            db.session.bulk_save_objects([Account(**row) for row in reader])
            db.session.commit()
        else:
            raise Exception(
                'The uploaded file is an empty instance of FileStorage.'
            )
