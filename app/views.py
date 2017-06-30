from flask import render_template, session, request, jsonify
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
    return render_template('index.html', form=form, log_text='')

@app.route('/addinput', methods=['POST'])
def addinput():
    global output
    global dictionary
    global stack
    new_input = request.form['input_stream']

    new_input = " ".join(new_input.split())
    print(" new_input is ", new_input)

    dictionary, stack, output = webrepl(new_input, dictionary, stack)
    print(" output is ", output)
    print(" stack is ", stack)
    cumulative_log.append(new_input)
    cumulative_log.append(output)
    return jsonify(new_input=new_input, output=output)
