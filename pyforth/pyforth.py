import sys, io
from contextlib import redirect_stdout

################### PARAM STACK ###################
stack = [] # using stack[-1] instead of a stack pointer

def print_stack():
    global output
    stri = ""
    stri = stri + "<" + str(len(stack)) + "> "
    for item in stack:
        stri = stri + str(item) + " "
    output += stri

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
index2 = None

dictionary = []

class EntryHeader():
    def __init__(self, name, immediate_flag, link_address):
        self.name = name
        self.immediate_flag = immediate_flag
        self.link_address = link_address

def print_dictionary(last_section_only=0):
    if last_section_only == 1:
        start = len(dictionary) - 20
    else:
        start = 0
    for i in range(start, len(dictionary)):
        if isinstance(dictionary[i], EntryHeader):
            cell = str(dictionary[i].name) + str(dictionary[i].immediate_flag) + " " + str(dictionary[i].link_address)
        else:
            cell = dictionary[i]
        x = ""
        if cell != 0 and isinstance(cell, int):
            x = "    | " + str(dictionary[cell]) + str(dictionary[cell].name)
        print(i, cell, x)


#####################  ADDING TO DICTIONARY  ######################

def HERE():
    push(len(dictionary) - 1)

def set_LATEST():
    global LATEST
    HERE()
    LATEST = pop()

def change_PC(index):
    global PC
    PC = index

def comma():
    tos = pop()
    dictionary.append(tos)
    HERE()

def _comma(entry):
    dictionary.append(entry)
    HERE()

def create(name, immediate_flag):
    new_entry_header = EntryHeader(name, immediate_flag, LATEST)
    dictionary.append(new_entry_header)
    set_LATEST()

def add_word(name, immediate_flag, code_pointer, data_field):
    create(name, immediate_flag) # adds name, imm flag, link address, and updates latest
    _comma(code_pointer)
    if data_field and len(data_field) == 1:
        _comma(data_field)
    elif data_field and len(data_field) > 1:
        for word in data_field:
            push(word)
            find()
            _comma(pop())#assume it is found for now
        _comma(exit)
    HERE()

def store():
    address = pop()
    contents = pop()
    dictionary[address] = contents

def fetch():
    address = pop()
    contents = dictionary[address]
    push(contents)

def find():
    new_word = pop()
    current_index = LATEST
    while current_index != None: # None means we are at the first word in the dictionary
        current = dictionary[current_index]
        if current.name == new_word:
            push(current_index)
            if current.immediate_flag == 1:
                push(-1)
            else:
                push(1)
            return
        current_index = current.link_address
    push(new_word)
    push(0)

################### COMPILING AND INTERPRETING ##############################

def exit():
    change_PC(pop_RS()) # set PC to top of return stack
    if PC != None: # if we are returning to a composite word thread
        next_word() # next word takes us to the next word in the composite word thread

def enter():
    push_RS(PC) # push PC to return stack so we can return to it
    change_PC(index) # set PC to current index/ address in the dictionary
    next_word()

def next_word():
    if PC != None:
        change_PC(PC + 1)
        push(PC)
        execute()

def execute():
    global index
    header_location = pop()
    code_pointer_location = header_location + 1
    if isinstance(dictionary[code_pointer_location], int):
        index = dictionary[code_pointer_location] + 1
    elif not isinstance(dictionary[code_pointer_location], int):
        index = code_pointer_location
    word_trace.append(dictionary[index])
    dictionary[index]()

def get_word():
    global input_stream
    word = input_stream[0].strip()
    input_stream = input_stream[1:]
    return word

def number():
    str_number = pop()
    number = int(str_number)
    push(number)

def interpret_word():
    word = get_word()
    find()
    tos = pop()
    if tos == 1 or tos is -1: # word was found, execute in interpret mode regardless of immediate flag
        execute()
    else:
        number()

def set_interpret():
    global STATE
    STATE = 0

def set_compile():
    global STATE
    STATE = 1

def colon():
    set_compile()
    add_word(None, 0, enter, None)

def semicolon():
    set_interpret()
    _comma(exit)

def compile_word():
    word = get_word()
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

"""def doliteral():
    print('in doliteral, going to push: ', dictionary[index+1])
    push(int(dictionary[index+1])) # ### index2 ? push number stored in the cell after doliteral code pointer
    change_PC(PC + 1) # increment PC by 1 (next_word will increment it by one again)
    next_word()

def literal():
    x = pop()
    dictionary.append(doliteral)
    dictionary.append(x)

def variable():
    push(index-1) ### index2 ?
"""
def quit():
    return_stack = []
    global input_stream
    input_stream = input_stream.split()
    print('input stream: ', input_stream)
    while len(input_stream):
        if STATE:
            compile_word()
        else:
            interpret_word()


"""################### BRANCHING AND LOOPING ##############################
# The cells after Qbranch and branch will store the index/ address to jump to
# if jumping past the current block
def if_():
    _comma(Qbranch)
    _comma(None)
    push(len(dictionary)-1)

def else_():
    _comma(branch)
    _comma(None)
    push(len(dictionary)-1)

def then():
    # left on the stack from if and else: @if @else
    dup()   # @Qbranch+1  @branch+1  @branch+1
    push(1) # @Qbranch+1  @branch+1  @branch+1   1
    sub()   # @Qbranch+1  @branch+1  @branch
    rot()   # @branch+1   @branch    @Qbranch+1
    rot()   # @branch-1   @Qbranch+1 @branch+1
    push(len(dictionary)) # @branch-1  @Qbranch+1  @branch+1   @then/exit
    swap()                # @branch-1  @Qbranch+1  @then/exit  @branch+1
    store() # ->> @then/exit stored at @branch+1
    store() # ->> @branch stored at @Qbranch+1


def Qbranch():
    global PC
    # Increment the PC by 1 -> it will point to the cell directly after Qbranch,
    # which stores the index/ address that points to the index/ address to jump to
    PC = PC + 1
    x = pop()
    push_RS(x) # put in return stack so branch can check it later
    if x != 0: # true -> carry out first block
        PC = PC + 1 # PC increments by one to enter first block
        push(PC)
        execute()
    else:
        # PC will point to index/ address saved in cell after qbranch
        PC = dictionary[PC]
        push(PC)
        execute()

def branch():
    global PC
    x = pop_RS()
    if x == 0: # false -> will carry out second block
        # skip cell after - which contains index/ address of exit
        PC = PC + 2
        push(PC)
        execute()
    else:
        # go to exit index/ address stored in the cell after branch
        PC = dictionary[PC+1]
        push(PC)
        execute()

def begin_():
    push_RS(index2) # store BEGIN's addr in the RS, so we can return to it if we repeat the loop
    next_word()

def until():
    global PC
    addr = pop_RS()
    flag = pop()
    if flag == 0:
        PC = addr - 1 # set PC to one less than BEGIN's addr (next_word will add 1)
    next_word()

def do():
    I = pop()
    J = pop()
    addr = index2
    push_RS(addr)
    push_RS(J)
    push_RS(I)
    next_word()

def loop():
    global PC
    I = pop_RS()
    J = pop_RS()
    addr = pop_RS()
    I = I + 1
    if I != J: # check loop should be repeated
        PC = addr - 1
        push(J)
        push(I)
    next_word()

def plus_loop():
    global PC
    I = pop_RS()
    J = pop_RS()
    addr = pop_RS()
    difference = pop()
    I = I + difference
    if I != J: # check if loop should be repeated
        PC = addr - 1
        push(J)
        push(I)
    next_word()

def I():
    I = return_stack[-1]
    push(I)
    next_word()
"""
def bye():
    global running
    running = False

################### NATIVE STACK MANIPULATION FUNCTIONS ###################

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

################ ADD NATIVE WORDS TO DICTIONARY ####################
add_word('.S', 0, print_stack, [])
add_word('DUP', 0, dup, [])
add_word('*', 0, mul, [])
add_word('+', 0, add, [])
add_word('-', 0, sub, [])
add_word('/', 0, div, [])
add_word('=', 0, equals, [])
add_word('<', 0, lessthan, [])
add_word('>', 0, greaterthan, [])
add_word(':', 1, colon, [])
add_word(';', 1, semicolon, [])
add_word('!', 0, store, [])
add_word('@', 0, fetch, [])
add_word('FIND', 0, find, [])
add_word('NUMBER', 1, number, None)
"""add_word('>R', 1, push_RS, None)
add_word('R>', 1, pop_RS, None)
add_word(',', 1, comma, None)
add_word('IF', 1, if_, None)
add_word('ELSE', 1, else_, None)
add_word('THEN', 1, then, None)
add_word('BRANCH', 0, branch, None)
add_word('QBRANCH', 0, Qbranch, None)
add_word('BEGIN', 0, begin_, None)
add_word('UNTIL', 0, until, None)
add_word('[', 0, set_interpret, None)
add_word(']', 0, set_compile, None)
add_word('BYE', 0, bye, None)
add_word('DO', 0, do, None)
add_word('LOOP', 0, loop, None)
add_word('+LOOP', 0, plus_loop, None)
add_word('I', 0, I, None)
add_word('.D', 0, print_dictionary, [])"""


def print_debug(): # FOR DEBUGGING
    print(' [index2, index, dictionary[index]] [PC] [stack]   [return_stack] ')
    for line in word_trace:
        print(line)


################# FOR RUNNING REPL #################

input_stream =  "1 2 3 + .S"
output = ""

def webrepl(input_line, consistent_dictionary, consistent_stack):
    global input_stream
    input_stream = input_line
    global stack
    stack = consistent_stack
    global output
    output = ""

    if consistent_dictionary != {}:
        global dictionary
        dictionary = consistent_dictionary

    quit()

    return dictionary, stack, output


if __name__ == "__main__":
    # if there is a forth file, open that
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        filetext = open(filename, 'r')
        for line in filetext:
            input_stream = input_stream + line.strip() + " "
        print('INPUT STREAM: ', input_stream)

    # run the forth from the file
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
