from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import SubmitField, FileField, RadioField
# from wtforms.validators import


class NameForm(FlaskForm):
    filefield = FileField('Choose the CSV file to perform fit to:',
                          validators=[FileRequired(),
                                      FileAllowed(['csv'],
                                                  message='Must\
                                                  be a csv file')])
    fitter = RadioField('Fitter', choices=[('1', 'Laurdan'), ('2', 'MC540')],
                        default='1')
    submit = SubmitField('Submit')
