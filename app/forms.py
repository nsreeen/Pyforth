from flask_wtf import Form
from wtforms import BooleanField, TextAreaField
from wtforms.validators import DataRequired

class ModeForm(Form):
    mode = BooleanField()

class CompileForm(Form):
    input_stream = TextAreaField('input_string', validators=[DataRequired()])
