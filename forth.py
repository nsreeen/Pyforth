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
    for i, cell in enumerate(dictionary):
        print(i, cell)


# NATIVE DICTIONARY FUNCTIONS
def variable():
    push(index2-1)

def dup():
    top = stack[SP]
    push(top)
    next_word()

def rot():
    """
    1 2 3
    2 3 1
    """
    three = pop()
    two = pop()
    one = pop()
    push(two)
    push(three)
    push(one)

def swap():
    """
    2 1
    1 2
    """
    one = pop()
    two = pop()
    push(one)
    push(two)

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
    print('\n @@@@@ IN SUB A, B, RESULT : ')
    b = pop() # second number
    a = pop() # first number
    result = a - b
    print(a, b, result)
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
    print('in execute, index, index2, point_to, dictionary[point_to] : ', index, index2, point_to, dictionary[point_to])
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
    print('/n in interpret word')
    get_word()
    find()
    print_stack()
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
    print('SEMI COLOn!')
    set_interpret()
    #dictionary.append(exit)
    push(exit)
    comma()

def compile_word():
    get_word()
    word = pop()

    push(word)
    find()

    found = pop()

    print('\n\n\n in compile word, word and found : ', word, found)

    if found < 0:
        print('immediate flag, will execute')
        execute()

    elif dictionary[-4] == None:
        print('creat header')
        dictionary[-4] = word
        pop()

    elif found == 1:
        comma()

    else:
        literal()



    """if dictionary[-4] == None:
        dictionary[-4] = word
    else:
        push(word)
        find()
        found = pop()
        if found == -1:
            execute()
        elif found == 1:
            comma()"""

def PCfunc(): #this is what PC would do in forth?!
    push('PC')
    find()

def doliteral():
    print('\n\nin doliteral, index and index2 and PC : ', index, index2, PC)
    print('will push: ', (dictionary[index2+1]))
    push(dictionary[index2+1])
    global PC
    PC = PC + 1
    next_word()

def literal():
    x = pop()
    dictionary.append(doliteral)
    dictionary.append(x)


def if_():
    dictionary.append(Qbranch)
    dictionary.append(None)
    push(len(dictionary)-1) ##### CHECK THIS

def else_():
    dictionary.append(branch)
    #print('in else')
    #print_dictionary()
    dictionary.append(None)
    push(len(dictionary)-1)
    #print(';len dict : ', len(dictionary))
    #push(len(dictionary)-2) ##### CHECK THIS

def Qbranch():
    global PC
    PC = PC + 1
    x = pop()
    push_RS(x)
    print('in qbranch, PC +1, x :', PC, x)
    if x != 0: #true - carry out first block
        print('TRUE')
        PC = PC + 1
        push(PC)
        execute()
    else:
        print('FALSE')
        PC = dictionary[PC]
        push(PC)
        execute()

def branch():
    global PC
    print('in branch, PC is', PC)
    x = pop_RS()
    if x == 0:
        print('FALSE')
        PC = PC + 2
        push(PC)
        execute()
    else:
        print('TRUE')
        PC = dictionary[PC+1]
        push(PC)
        execute()

def then():
    print('\n\n\n IN THEN, THE STACK: ')
    print_stack()
    dup()
    push(1)
    sub()
    rot()
    rot()
    print_stack()
    print('len(dictionary) is ', len(dictionary) )
    push(len(dictionary))
    swap()
    print_stack()
    store()
    store()

"""77 THEN
78 1
79 75
80 <function then at 0x7f84af538d90>
81 BRANCH
82 0
83 79
84 <function branch at 0x7f84af538d08>
85 QBRANCH
86 0
87 83
88 <function Qbranch at 0x7f84af538c80>
89 TEST
90 0
91 87
92 <function enter at 0x7f84af538268>
93 <function Qbranch at 0x7f84af538c80> #here we append address ( current + 1 -> index a )
94 98 -->97
95 <function doliteral at 0x7f84af538a60>
96 7
97 <function branch at 0x7f84af538d08> #here we append address  ( current -> index b )
98 101
99 <function doliteral at 0x7f84af538a60>
100 100
101 <function exit at 0x7f84af5381e0>  # then pushes this index to stack ( index c )

a  b
93 97
b  a  c  b
97 93 101 97
IF 5 ELSE 1 THEN

IF -> writes function pointer to Qbranch, leaves a cell blank (index a), pushes the indes to stack
action fills however many cells
ELSE -> writes function pointer to branch, leaves a cell blank (index b), pushes index to stack
action fills however many cells
THEN -> (index c)

THEN:
stack: a b
DUP
a b b
1 -
a b b-1
ROT
b b-1 a
ROT
b-1 a b
push current
b a b c
SWAP
b a c b
                        val  addr  val addr
                        97    94    101   98
stack should look like: b-1    a     c    b
STORE -> put c in b    (b is val, c is addr)
STORE -> put b-1 in a    ( is val, c is addr)

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
add_word('IF', 1, if_, None)
add_word('ELSE', 1, else_, None)
add_word('THEN', 1, then, None)
add_word('BRANCH', 0, branch, None)
add_word('QBRANCH', 0, Qbranch, None)

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


input_stream = ": TEST IF 7 ELSE 100 THEN ; 1 TEST "
#input_stream = ": TWICE DUP + DUP ; : SQUARED DUP * ; : CUBED DUP SQUARED * ; 2 CUBED 3 SQUARED 5 TWICE .S "
quit()
print_dictionary
