from flask import render_template, session, request, jsonify
from app import app
from pyforth.pyforth import webrepl
from .forms import ModeForm, CompileForm
import re

#cumulative_log = []
#dictionary = {}
#stack = []

@app.route('/', methods=['GET', 'POST'])
def index():
    form = CompileForm()
    return render_template('index.html', form=form, log_text='')

@app.route('/visualizer', methods=['GET', 'POST'])
def visualizer():
    form = CompileForm()
    return render_template('visualizer.html', form=form, log_text='')

@app.route('/sendinput', methods=['POST'])
def sendinput():
    print('IN SEND INPUT')
    #global dictionary
    #global stack
    inp = request.form
    input_lines = inp.getlist('input_lines[]')
    #all_input =str(request.form['input_lines']) # <-------------- because its an array now?
    #print(" all_input is ", all_input)
    #all_input = " ".join(input_lines) #.split())
    print(" input_lines is ", input_lines)

    output_lines = webrepl(input_lines)
    print(" output_lines is ", output_lines)
    return jsonify(input_lines=input_lines, output_lines=output_lines)
