import sys, io
from contextlib import redirect_stdout

################### PARAM STACK ###################
stack = [] # using stack[-1] instead of a stack pointer

def push(item):
    stack.append(item)

def pop():
    tos = stack.pop()
    return tos

################### RETURN stack ###################
return_stack = []

def push_RS(item):
    return_stack.append(item)

def pop_RS():
    tos = return_stack.pop()
    return tos

################### Dictionary ###################
word_trace = [] #for debugging
STATE = 0 # 0 means interpret mode

LATEST = None
PC = None
index = None

def HERE():
    push(len(dictionary) - 1)

def update_LATEST():
    global LATEST
    HERE()
    LATEST = pop()

def update_PC(new_PC):
    global PC
    PC = new_PC

def update_index(new_index):
    global index
    index = new_index

dictionary = []

class WordHeader():
    def __init__(self, name, immediate_flag, link_address):
        self.name = name
        self.immediate_flag = immediate_flag
        self.link_address = link_address


#####################  ADDING TO DICTIONARY  ######################

def comma():
    tos = pop()
    dictionary.append(tos)

def _comma(entry):
    dictionary.append(entry)

def add_word_header(name, immediate_flag):
    new_word_header = WordHeader(name, immediate_flag, LATEST)
    dictionary.append(new_word_header)
    update_LATEST()

def add_word(name, code_pointer, immediate_flag=0, data_field=None):
    add_word_header(name, immediate_flag) # adds name, imm flag, link address, and updates latest
    _comma(code_pointer)
    if data_field and code_pointer == variable:
        _comma(data_field)
    elif data_field:
        for word in data_field:
            push(word)
            find()
            pop() #assume it is found for now
            _comma(pop())
        _comma(exit)

def find():
    word = pop()
    current_index = LATEST
    while current_index != None: # None means we are at the first word in the dictionary
        current = dictionary[current_index]
        if current.name == word:
            push(current_index)
            if current.immediate_flag == 1:
                push(-1)
            else:
                push(1)
            return
        current_index = current.link_address
    push(word)
    push(0)

################### INTERPRETING AND COMPILING ##############################

def quit():
    return_stack = []
    global input_stream
    input_stream = input_stream.split()
    while len(input_stream):
        if STATE:
            compile_word()
        else:
            interpret_word()

def interpret_word():
    get_word()
    print('\n word is: ', stack[-1])
    find()
    found = pop()
    if found == 1 or found is -1: # word was found, execute in interpret mode regardless of immediate flag
        execute()
    else:
        number()

def get_word():
    global input_stream
    word = input_stream[0].strip()
    input_stream = input_stream[1:]
    push(word)

def number():
    str_number = pop()
    number = int(str_number)
    push(number)

def execute():
    addr = pop()

    # addr itself contains an int ie another address
    if isinstance(dictionary[addr], int):
        update_index(dictionary[addr]+1)

    # assume cell after addr is an int
    else:
        update_index(addr+1)

    dictionary[index]()

def set_interpret():
    global STATE
    STATE = 0

def set_compile():
    global STATE
    STATE = 1

def colon():
    set_compile()
    add_word(None, enter)

def semicolon():
    set_interpret()
    _comma(0) # index of exit word header

def compile_word():
    get_word()
    word = pop()
    if dictionary[LATEST].name == None:
        dictionary[LATEST].name = word
    else:
        push(word)
        find()
        found = pop()
        if found < 0: # word has an immediate flag
            execute()
        elif found == 1: # no immediate flag, word should be compiled
            comma()
        else:
            literal() # word isn't found, it is a number

def doliteral():
    number = int(dictionary[index+1])
    push(number)
    update_PC(PC + 1) # because the next cell is the number
    next_word()

def literal():
    x = pop()
    _comma(doliteral)
    _comma(x)

################### THREADING ##############################

def exit():
    print('in exit, PC is ', PC)
    update_PC(pop_RS()) # set PC to top of return stack
    if PC != None: # if we are returning to a composite word thread
        next_word() # next word takes us to the next word in the composite word thread

def enter():
    print('in enter, PC is ', PC)
    push_RS(PC) # push PC to return stack so we can return to it
    update_PC(index) # set PC to current index/ address in the dictionary
    next_word()

def next_word():
    print('in next_word, PC is ', PC)
    if PC != None:
        update_PC(PC + 1)
        push(PC)
        execute()

################### NATIVE FUNCTIONS ###################
def bye():
    global running
    running = False

def dup():
    top = stack[-1]
    push(top)
    next_word()

def rot():
    # 1 2 3 -> 2 3 1
    three = pop()
    two = pop()
    one = pop()
    push(two)
    push(three)
    push(one)

def swap():
    # 2 1 -> 1 2
    one = pop()
    two = pop()
    push(one)
    push(two)

def mul():
    a = pop()
    b = pop()
    push(a * b)
    next_word()

def add():
    a = pop()
    b = pop()
    push(a + b)
    next_word()

def sub():
    b = pop() # second number
    a = pop() # first number
    push(a - b)
    next_word()

def div():
    a = pop()
    b = pop()
    push(a / b)
    next_word()

def equals():
    a = pop()
    b = pop()
    if a == b:
        push(1)
    else:
        push(0)
    next_word()

def lessthan():
    b = pop()
    a = pop()
    if a < b:
        push(1)
    else:
        push(0)
    next_word()

def greaterthan():
    b = pop()
    a = pop()
    if a > b:
        push(1)
    else:
        push(0)
    next_word()

def store():
    address = pop()
    contents = pop()
    dictionary[address] = contents

def fetch():
    address = pop()
    contents = dictionary[address]
    push(contents)

#################### PRINTING AND DEBUGGING ###################
def print_stack():
    global output
    stri = ""
    stri = stri + "<" + str(len(stack)) + "> "
    for item in stack:
        stri = stri + str(item) + " "
    output += stri

def print_dictionary(last_section_only=0):
    if last_section_only == 1:
        start = len(dictionary) - 20
    else:
        start = 0
    for i in range(start, len(dictionary)):
        if isinstance(dictionary[i], WordHeader):
            cell = str(dictionary[i].name) + " " + str(dictionary[i].immediate_flag) + " " + str(dictionary[i].link_address)
        else:
            cell = dictionary[i]
        x = ""
        if cell != 0 and isinstance(cell, int):
            x = "    | " + str(dictionary[cell]) + str(dictionary[cell].name)
        print(i, cell, x)


################ ADD NATIVE WORDS TO DICTIONARY ####################
"""add_word('.S', print_stack)
add_word('DUP', dup)
add_word('*', mul)
add_word('+', add)
add_word('-', sub)
add_word('/', div)
add_word('=', equals)
add_word('<', lessthan)
add_word('>', greaterthan)
add_word('BYE', bye)
add_word(':', colon, immediate_flag = 1)
add_word(';', semicolon, immediate_flag = 1)
add_word('!', store)
add_word('@', fetch)"""

words_to_add_to_dictionary = [('EXIT', exit),
('.S', print_stack), ('DUP', dup), ('*', mul),
('+', add), ('-', sub), ('/', div), ('<', lessthan), ('>', greaterthan),
('BYE', bye), (':', colon, 1), (';', semicolon, 1), ('!', store), ('@', fetch),
('.D', print_dictionary)]

for word in words_to_add_to_dictionary:
    name = word[0]
    code_pointer = word[1]
    if len(word) > 2:
        immediate_flag = word[2]
    else:
        immediate_flag = 0
    add_word(name, code_pointer, immediate_flag)

#########################################

input_stream = ""


if __name__ == "__main__":
    # if there is a forth file, open that
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        filetext = open(filename, 'r')
        for line in filetext:
            input_stream = input_stream + line.strip() + " "

        quit()

    # start the repl
    running = True
    while running:
        input_stream = input()
        if input_stream:
            #try:
            output = ""
            quit()
            print("".join(output))
            #except:
            #    print('word not in dictionary')
