import sys

################### PARAM STACK ###################
stack = []
# for now, instead of using a stack pointer, will just use stack[-1]
# later - maybe add a slot at the start of the dictionary to store this?

def print_stack():
    stri = ""
    stri = stri + "<" + str(len(stack)) + "> "
    for item in stack:
        stri = stri + str(item) + " "
    print(stri)
    global output
    output = stri

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
#state could also be in the dictionary? should all (state pc etc) be? need a way to get them?

# Store HERE, LATEST, PC, index, index2 - as first three entries in the dictionary
dictionary = ['HERE', -1, 'LATEST', -1, 'PC', -1] #, 'index', -1, 'index2', -1]

index = None # way to keep track of the 'address' index - work around because using python
index2 = None

def print_dictionary(last_section_only=0):
    if last_section_only == 1:
        start = len(dictionary) - 15
    else:
        start = 0

    for i in range(start, len(dictionary)):
        cell = dictionary[i]
        x = ""
        if cell != 0 and isinstance(cell, int):
            x = "    | " + str(dictionary[cell])
        print(i, cell, x)

################### NATIVE FUNCTIONS FOR ADDING TO DICTIONARY  ###################

def comma():
    tos = pop()
    dictionary.append(tos)
    dictionary[1] = len(dictionary) - 1 # HERE - not really necessary as not using it to add

def add_word(name, immediate_flag, code_pointer, data_field):
    create(name, immediate_flag) # adds name, imm flag, link address, and updates latest

    if code_pointer == variable:
        push(variable)
        comma()
        push(data_field)
        comma()

    elif code_pointer != None: # it is a link, this is not a composite word
        push(code_pointer)
        comma()

    else: # this is a composite word
        push(enter)
        comma()
        for word in data_field:
            push(word)
            find()
            found = pop() #assume it is found for now
            comma()

        push(exit)
        comma()

    dictionary[1] = len(dictionary) - 1 # HERE

def create(name, immediate_flag):
    push(name)
    comma()
    push(immediate_flag)
    comma()
    push(dictionary[3]) #LATEST is pushed as link address
    comma()
    dictionary[3] = len(dictionary) - 1 # LATEST is updated

def store():
    address = pop()
    contents = pop()
    dictionary[address] = contents

def fetch():
    address = pop()
    contents = dictionary[address]
    push(contents)

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

def ifdup():
    top = stack[SP]
    if top != 0:
        push(top)
    next_word()

################### COMPILING AND INTERPRETING ##############################

def exit():
    tors = pop_RS()
    dictionary[5] = tors
    if dictionary[5] != -1:
        next_word()

def enter():
    push_RS(dictionary[5])
    dictionary[5] = index
    next_word()

def next_word():
    if dictionary[5] != -1: # so that it only does anything if we r in a thread
        # ie if PC is being used to store our place in a thread?
        # there must be a more elegant solution?!?!
        dictionary[5] = dictionary[5] + 1
        push(dictionary[5])
        execute()

def execute():
    tos = pop()
    # index and index2 used because no way to reliably get address r index from value.
    # So we need another way to keep track of where in the dictionary we are and how we got there.
    global index
    global index2
    index2 = tos # index2 keeps track of where we are in the dictionary before
    # we potentially follow an index looking for a function pointer
    # not using PC for this because whether or not PC is being used determines
    # whether or not next_word does anything
    point_to = None

    if not isinstance(dictionary[tos], int):
        # The cell contains the function pointer we want.
        index = tos

    else:
        # The cell contains the index of another cell, which contains the function pointer we want.
        index = dictionary[tos]

    word_trace.append([[index2, index, dictionary[index]], [dictionary[5]], stack[:], return_stack[:]]) # for debgging

    print('in execute, index is ', index, ' func is: ', dictionary[index])
    dictionary[index]() # execute the function we want

def get_word():
    global input_stream
    new_word = ""
    c = ""
    while c != " " and len(input_stream) > 0:
        c = input_stream[0]
        new_word = new_word + c
        input_stream = input_stream[1:]
    push(new_word)

def find():
    #print('(((((((((((((((( in FIND ', dictionary[3])
    new_word = pop()
    #print('new word is ', new_word)
    current_link_index = dictionary[3] #LATEST
    while current_link_index != -1:
        #print('current_link_index : ', current_link_index)
        current_name = dictionary[current_link_index-2]
        #print('current name : ', current_name, ' new_word: ', new_word)
        ##print('\n\n in find, looping through linked list')
        ##print('word to find, current name, current_link_index : ', new_word, current_name, current_link_index)
        if current_name.strip() == new_word.strip():
            push(current_link_index + 1)
            ##print('FOUND: word and link to be sent for it: ', new_word, current_link_index+1)
            #print_dictionary()
            if dictionary[current_link_index-1] == 1:
                push(-1)
            else:
                push(1)
            return
        current_link_index = dictionary[current_link_index]
    push(new_word)
    push(0)

def number():
    string = pop()
    number = int(string)
    push(number)

def interpret_word():
    get_word()
    word = stack[-1]
    find()
    tos = pop()
    if tos == 1 or tos is -1:
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
    create('/', 0)

def semicolon():
    set_interpret()
    push(exit)
    comma()

def compile_word():
    get_word()
    word = pop()
    if dictionary[-3] == '/':
        dictionary[-3] = word
        push(enter)
        comma()
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
    push(int(dictionary[index2+1]))
    dictionary[5] = dictionary[5] + 1
    next_word()

def literal():
    x = pop()
    dictionary.append(doliteral)
    dictionary.append(x)

def variable():
    push(index2-1)

def quit():
    global return_stack
    return_stack = []
    while len(input_stream):
        if STATE:
            compile_word()
        else:
            interpret_word()


################### BRANCHING AND LOOPING ##############################

def if_():
    push(Qbranch)
    comma()
    push(None)
    comma()
    push(len(dictionary)-1) ##### CHECK THIS

def else_():
    push(branch)
    comma()
    push(None)
    comma()
    push(len(dictionary)-1)

def Qbranch():
    dictionary[5] = dictionary[5] + 1 # increment the PC
    x = pop()
    push_RS(x) # store in return stack so branch can check it later
    if x != 0: # true - carry out first block
        dictionary[5] = dictionary[5] + 1 # PC increments by one to enter first block
        push(dictionary[5])
        execute()
    else:
        dictionary[5] = dictionary[dictionary[5]] # PC becomes index saved in cell after qbranch
        push(dictionary[5])
        execute()


def branch():
    x = pop_RS()
    if x == 0: # will carry out second block
        dictionary[5] = dictionary[5] + 2
        push(dictionary[5])
        execute()
    else:
        dictionary[5] = dictionary[dictionary[5]+1]
        push(dictionary[5])
        execute()

def then():
    dup()
    push(1)
    sub()
    rot()
    rot()
    push(len(dictionary))
    swap()
    store()
    store()

def begin_():
    push_RS(index2) # store BEGIN's addr in the RS, so we can return to it if we repeat the loop
    next_word()

def until():
    addr = pop_RS()
    flag = pop()
    compare = pop()
    if flag != compare:
        #print('continue')
        dictionary[5] = addr - 1 # set PC to one less than BEGIN's addr
    next_word()

def while_():
    addr = pop_RS()
    flag = pop()
    compare = pop()
    if flag == compare:
        #print('continue')
        dictionary[5] = addr - 1 # set PC to one less than BEGIN's addr
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
    I = pop_RS()
    J = pop_RS()
    addr = pop_RS()
    I = I + 1
    if I != J:
        # return to do
        dictionary[5] = addr - 1
        push(J)
        push(I)
    next_word()

def plus_loop():
    I = pop_RS()
    J = pop_RS()
    addr = pop_RS()
    difference = pop()
    I = I + difference
    if I != J:
        # return to do
        dictionary[5] = addr - 1
        push(J)
        push(I)
    next_word()

def I():
    I = pop_RS()
    push(I)
    push_RS(I)
    next_word()

def bye():
    global running
    running = False


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
add_word('>R', 1, push_RS, None)
add_word('R>', 1, pop_RS, None)
add_word(',', 1, comma, None)
add_word('IF', 1, if_, None)
add_word('ELSE', 1, else_, None)
add_word('THEN', 1, then, None)
add_word('BRANCH', 0, branch, None)
add_word('QBRANCH', 0, Qbranch, None)
add_word('BEGIN', 0, begin_, None)
add_word('WHILE', 0, while_, None)
add_word('UNTIL', 0, until, None)
add_word('[', 0, set_interpret, None)
add_word(']', 0, set_compile, None)
add_word('BYE', 0, bye, None)
add_word('DO', 0, do, None)
add_word('LOOP', 0, loop, None)
add_word('+LOOP', 0, plus_loop, None)
add_word('I', 0, I, None)


def print_debug(): # FOR DEBUGGING
    print(' [index2, index, dictionary[index]]            [PC] [stack]   [return_stack] ')
    for line in word_trace:
        print(line)

input_stream = ""
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
    print('output is: ', output)
    return dictionary, stack, output

if __name__ == "__main__":
    input_stream = ": TEST 30 2 DO 2 I + DUP +LOOP ;"

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        filetext = open(filename, 'r')
        for line in filetext:
            input_stream = input_stream + line.strip() + " "
        #input_stream = filetext
        print('INPUT STREAM: ', input_stream)

    quit()
    running = True
    while running:
        input_stream = input()
        if input_stream:
            try:
                quit()
                print('ok')
            except:
                print('Undefined word')
