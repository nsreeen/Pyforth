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
    inp = request.form
    input_lines = inp.getlist('input_lines[]')
    output_lines, _ = webrepl(input_lines)
    return jsonify(input_lines=input_lines, output_lines=output_lines)

@app.route('/sendinputVisualizer', methods=['POST'])
def sendinputVisualizer():
    inp = request.form
    input_lines = inp.getlist('input_lines[]')
    output_lines, stack_lines = webrepl(input_lines)
    print(input_lines, output_lines, stack_lines)
    return jsonify(input_lines=input_lines, output_lines=output_lines, stack_lines=stack_lines)
