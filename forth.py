# PARAM STACK
stack = []
SP = None

def print_stack():
    print('\n Param stack: ')
    for slot in reversed(stack):
        print(slot)
    print('\n Return stack: ')
    for slot in reversed(return_stack):
        print(slot)

def push(item):
    stack.append(item)
    global SP
    SP = len(stack) - 1

def pop():
    tos = stack.pop()
    global SP
    SP = len(stack) - 1
    return tos

# RETURN stack
return_stack = []
RP = None

def push_RS(item):
    return_stack.append(item)
    global RP
    RP = len(return_stack) - 1

def pop_RS():
    tos = return_stack.pop()
    global RP
    RP = len(return_stack) - 1
    return tos

# Dictionary

STATE = 0 # 0 means interpret mode

dictionary = []

index = None # way to keep track of the 'address' index - work around because using python
index2 = None
PC = None

latest = None # will hold link address (index) for previous word once words added

here = None # holds index of last added to dictionary (prob not necessary in python)
# not using it now because using append instead

def add_word(name, immediate_flag, code_pointer, data_field):
    #print('adding name to dict ', name)
    global latest
    dictionary.append(name)
    dictionary.append(immediate_flag)
    dictionary.append(latest)
    #print('in add word:  name, len dict :', name, len(dictionary) )
    placer_for_latest = len(dictionary) - 1 #  index of last cell added (holds link address to previous entry)

    if code_pointer == variable:
        dictionary.append(variable)
        dictionary.append(data_field)

    elif code_pointer != None: # tlatest is a link, this is not a composite word
        dictionary.append(code_pointer)

    else: # this is a composite word
        dictionary.append(enter) # enter will be code pointer for composite words
        for word in data_field:
            push(word)
            find()
            found = pop()
            #if found == 0:
            #print('PROBLEM FINDING WORD - FIND PUSHED 0 TO STACK')
            link = pop()
            #print('>>>>>>>>>>> adding word list, word in word list, link found: ', word, link)
            #print('in add word, adding composite \n found word from word list: ', word, link)
            dictionary.append(link)
        dictionary.append(exit)

    latest = placer_for_latest

    here = len(dictionary) - 1


def print_dictionary():
    pass
    #for i, cell in enumerate(dictionary):
    #    print(i, ': ', cell)

# NATIVE DICTIONARY FUNCTIONS
def variable():
    push(index2-1)

def dup():
    top = stack[SP]
    push(top)
    next_word()

def mul():
    a = pop()
    b = pop()
    result = a * b
    push(result)
    next_word()

def add():
    a = pop()
    b = pop()
    result = a + b
    push(result)
    next_word()

def sub():
    a = pop()
    b = pop()
    result = a - b
    push(result)
    next_word()

def div():
    a = pop()
    b = pop()
    result = a / b
    push(result)
    next_word()

def equals():
    a = pop()
    b = pop()
    if a == b:
        push(1)
    else:
        push(-1)
    next_word()

def store():
    address = pop()
    contents = pop()
    dictionary[address] = contents

def fetch():
    address = pop()
    contents = dictionary[address]
    push(contents)

def exit():
    global PC
    PC = pop_RS()
    if PC != None:
        next_word()

def enter():
    #print('#####in enter, PC  and index: ', PC, index, 'type pc', type(PC))
    global PC
    push_RS(PC)
    PC = index
    #print('#####in enter, PC  and index: ', PC, index, 'type pc', type(PC))
    next_word()

def next_word():
    global PC
    if PC != None: # so that it only does anything if we r in a thread
        # there must be a more elegant solution?!?!
        PC = PC + 1
        push(PC)
        execute()

def execute():
    tos = pop()
    global index2
    index2 = tos # this is a stop gap solution1!!!!!
    point_to = None

    if not isinstance(dictionary[tos], int):
        point_to = tos
        #print(' in not int tos, point to is : ', tos, point_to, type(point_to))
    else:
        point_to = dictionary[tos]
        #print(' in else ptos, oint to is : ', tos, point_to, type(point_to))
    global index
    index = point_to
    dictionary[point_to]()

def get_word():
    global input_stream
    new_word = ""
    while len(input_stream):
        new_word = new_word + input_stream[0]
        input_stream = input_stream[1:]
        if input_stream[0] == " ":
            input_stream = input_stream[1:]
            push(new_word)
            return
    push(new_word)

def find():
    new_word = pop()
    current_link_index = latest
    while current_link_index != None:
        current_name = dictionary[current_link_index-2]
        #print('\n\n in find, looping through linked list')
        #print('word to find, current name, current_link_index : ', new_word, current_name, current_link_index)
        if current_name== new_word:
            push(current_link_index + 1)
            #print('FOUND: word and link to be sent for it: ', new_word, current_link_index+1)
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
    find()
    tos = pop()
    if tos == 1 or tos is -1:
        execute()
    else:
        number()

def ifdup():
    top = stack[SP]
    if top != 0:
        push(top)
    next_word()

def comma():
    tos = pop()
    dictionary.append(tos)

def set_interpret():
    global STATE
    STATE = 0

def set_compile():
    global STATE
    STATE = 1

def colon():
    set_compile()
    global latest
    push(None)
    comma()
    push(0) # how can immediate flag be set to 0 for a dynamically added word?
    comma()
    push(latest)
    comma()

    placer_for_latest = len(dictionary) - 1 #  index of last cell added (holds link address to previous entry)
    push(enter)
    comma()

    latest = placer_for_latest
    here = len(dictionary) - 1

def semicolon():
    set_interpret()
    #dictionary.append(exit)
    push(exit)
    comma()

def compile_word():
    get_word()
    word = pop()
    if dictionary[-4] == None:
        dictionary[-4] = word
    else:
        push(word)
        find()
        found = pop()
        if found == -1:
            execute()
        elif found == 1:
            comma()

def PCfunc(): #this is what PC would do in forth?!
    push('PC')
    find()





"""
SO to change PC the forth way (so can switch out some words later):
push new value
call 'PCfunc' (which will result in PC index going on the stack)
call store
"""

"""
IF 5 ELSE 1 THEN

IF -> writes function pointer to branch, leaves a cell blank (index a), pushes the indes to stack
action fills however many cells
ELSE -> writes function pointer to zbranch, leaves a cell blank (index b), pushes index to stack
action fills however many cells
THEN -> (index c)

THEN:
stack: a b
DUP
a b b
ROT ROT (or -ROT?)
b a b
push current
b a b c
SWAP
stack should look like: b a c b
STORE -> c put in address b
STORE -> b put in address a

def if():
    dictionary.append(branch)
    dictionary.append(None)

def else():
    dictionary.append(zbranch)
    dictionary.append(None)

def branch():
    x = pop()
    if x != 0:
        PC = PC + 2
        push(PC)
        execute()
    else:
        address = dictionary[PC + 1]
        push(address)
        execute()

def zbranch():
    x = pop()
    if x == 0:
        PC = PC + 2
        push(PC)
        execute()
    else:
        address = dictionary[PC + 1]
        push(address)
        execute()

def then():
    dup()
    rot()
    rot()
    push(PC)
    swap()
    store()
    store()

cell1: if func -> if not 0 (true) skip one cell, else jumps to address in next cell
cell2: action
cell3: else func: if 0 (false) skips one cell, else jumps Y cells
cell4: action


"""

def quit():
    global return_stack
    return_stack = []
    while len(input_stream):
        if STATE:
            compile_word()
        else:
            interpret_word()

# Add some words to dictionary
add_word('.S', 0, print_stack, [])
add_word('DUP', 0, dup, [])
add_word('*', 0, mul, [])
add_word('+', 0, add, [])
add_word('-', 0, sub, [])
add_word('/', 0, div, [])
add_word('=', 0, equals, [])
add_word(':', 1, colon, [])
add_word(';', 1, semicolon, [])
add_word('!', 0, store, [])
add_word('@', 0, fetch, [])
add_word('FIND', 0, find, [])
add_word('NUMBER', 1, number, [])
add_word('>R', 1, push_RS, [])
add_word('R>', 1, pop_RS, [])
add_word(',', 1, comma, [])
add_word('PC', 0, variable, None)


### TESTS
def test_add_words():
    push(1)
    push(2)
    push(3)
    print('sp: ', stack[SP])
    pop()
    print_stack()
    print('sp: ', stack[SP])
    dup()
    mul()
    print_stack()


def test_linked_list():
    print('Test the linked list:')
    current = latest
    print(current)
    while current != None:
        current = dictionary[current]
        print(current)


input_stream = ": TWICE DUP + DUP ; : SQUARED DUP * ; : CUBED DUP SQUARED * ; 2 CUBED 3 SQUARED 5 TWICE .S "
#quit()
PCfunc()
for i, cell in enumerate(dictionary):
    print(i, cell)
print_stack()
print(pop())
execute()
