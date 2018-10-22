from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired

class ImportForm(FlaskForm):
    """
    CSV import form class.
    """

    file = FileField('file', validators=[
        FileRequired(),
        FileAllowed(['csv'])
    ])
