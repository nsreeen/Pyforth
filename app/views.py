from flask import render_template, session, request
from app import app
from pyforth.pyforth import webrepl
from .forms import ModeForm, CompileForm
import re

cumulative_log = []
dictionary = {}
stack = []
output = ""

@app.route('/', methods=['GET', 'POST'])
def index():
    form = CompileForm()
    global output
    global dictionary
    global stack
    if request.method == 'POST':
        if form.validate_on_submit():
            print(form)
            new_input_stream = form.input_stream.data
            form.input_stream.data = ''
            print(" new_input_stream is ", new_input_stream, "|")
            #new_input_stream = re.sub(new_input_stream, '\\n\\r', '0')
            new_input_stream = " ".join(new_input_stream.splitlines())
            print(" new_input_stream is ", new_input_stream, "|")

            dictionary, stack, output = webrepl(new_input_stream, dictionary, stack)
            cumulative_log.append(new_input_stream)
            cumulative_log.append(output)


            print(" output is ", output)
            print(" cumulative_log is ", cumulative_log)

            return render_template('index.html', form=form, log_text = cumulative_log)
    return render_template('index.html', form=form, log_text='')
