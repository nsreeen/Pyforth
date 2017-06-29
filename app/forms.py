from flask_wtf import Form
from wtforms import RadioField, TextAreaField
from wtforms.validators import DataRequired

class ModeForm(Form):
        mode = RadioField('mode', choices=[('compile', 'compile'),('interpret', 'interpret')], default='compile')

class CompileForm(Form):
    input_stream = TextAreaField('input_string', validators=[DataRequired()])
