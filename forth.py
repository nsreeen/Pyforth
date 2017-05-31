# PARAM STACK
stack = []
# for now, instead of using a stack pointer, will just use stack[-1]
# later - maybe add a slot at the start of the dictionary to store this?
def print_stack():
    print('\n Param stack: ')
    for slot in reversed(stack):
        print(slot)
    print('Return stack: ')
    for slot in reversed(return_stack):
        print(slot)
    print('\n')

def push(item):
    #print('\n IN PUSH')#, item, PC : ', item, PC)
    stack.append(item)

def pop():
    tos = stack.pop()
    #print('\n IN POP')#, popped, PC : ', tos, PC)
    return tos

# RETURN stack
return_stack = []
#RP = None

def push_RS(item):
    print('\n IN PUSH_RS')#, item, PC : ', item, PC)
    return_stack.append(item)


def pop_RS():
    tos = return_stack.pop()
    print('\n IN POP_RS')# , popped, PC : ', tos, PC)
    return tos

# Dictionary

STATE = 0 # 0 means interpret mode
#state could also be in the dictionary? should all (state pc etc) be 

# Store HERE, LATEST, PC as first three entries in the dictionary
dictionary = [-1, -1, -1]



index = None # way to keep track of the 'address' index - work around because using python
index2 = None
#dictionary[2] = None

latest = None # will hold link address (index) for previous word once words added

here = None # holds index of last added to dictionary (prob not necessary in python)
# not using it now because using append instead

def add_word(name, immediate_flag, code_pointer, data_field):
    print('IN ADD WORD ', name, '   PC: ', dictionary[2])
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
    print('IN VARIABLE index, index2: ', index, index2, '   dictionary[2]: ', dictionary[2])
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
    print('\n in equals ')
    a = pop()
    b = pop()
    print('a: ', a, type(a), ' b: ', b, type(b))
    print(' a == b ? : ', a==b)
    if a == b:
        push(1)
    else:
        push(0)
    print_stack()
    next_word()

def store():
    address = pop()
    contents = pop()
    print('IN STORE addr,contents : ', address, contents, ' index, index2: ', index, index2, '   dictionary[2]: ', dictionary[2])
    dictionary[address] = contents

def fetch():
    address = pop()
    contents = dictionary[address]
    print('IN FETCH addr,contents : ', address, contents, ' index, index2: ', index, index2, '   dictionary[2]: ', dictionary[2])
    push(contents)

def exit():
    print('IN EXIT top of RS : ', return_stack[-1], ' index, index2: ', index, index2, '   dictionary[2]: ', dictionary[2])
    #global dictionary[2]
    tors = pop_RS()
    #push(tors)
    #set_dictionary[2]()
    dictionary[2] = tors
    #if dictionary[2] != None:
    #    next_word()

def enter():
    print('IN ENTER, dictionary[2]  and index: ', ' index, index2: ', index, index2, '   dictionary[2]: ', dictionary[2])
    #global dictionary[2]
    push_RS(dictionary[2])
    dictionary[2] = index
    #print('#####in enter, dictionary[2]  and index: ', dictionary[2], index, 'type dictionary[2]', type(dictionary[2]))
    next_word()

def next_word():
    print('IN NEXT WORD, ', ' index, index2: ', index, index2, '   dictionary[2]: ', dictionary[2])
    #global dictionary[2]
    if dictionary[2] != -1: # so that it only does anything if we r in a thread
        # there must be a more elegant solution?!?!
        dictionary[2] = dictionary[2] + 1
        push(dictionary[2])
        execute()

def execute():
    tos = pop()
    print('IN EXECUTE tos: ', tos, ' index, index2: ', index, index2, '   dictionary[2]: ', dictionary[2])
    # index and index2 used because no way to reliably get address r index from value.
    # So we need another way to keep track of where in the dictionary we are and how we got there.
    global index
    global index2
    index2 = tos # index2 keeps track of outer index
    point_to = None

    if not isinstance(dictionary[tos], int):
        # The cell contains the function pointer we want.
        index = tos

    else:
        # The cell contains the index of another cell, which contains the function pointer we want.
        index = dictionary[tos]

    dictionary[index]()

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
    print('in FIND')
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
    print('in NUMBER')
    string = pop()
    number = int(string)
    push(number)

def interpret_word():
    get_word()
    print('/n in interpret word ', stack[-1])
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
    print('IN COMMA')
    tos = pop()
    dictionary.append(tos)

def set_interpret():
    print('set state -> 0')
    global STATE
    STATE = 0

def set_compile():
    print('set state -> 1')
    global STATE
    STATE = 1

def colon():
    print('IN COMPILE')
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

"""
: COLON
    SET-COMPILE
    // get rid of all the placer for latest stuff by using , to add everything to dict?
    // create will use , and , will update here
    CREATE
    @ ENTER ,


: SET-COMPILE 1 STATE ! ;

: SET-INTERPRET 0 STATE ! ;
"""
def semicolon():
    print('IN SEMI COLOn!')
    set_interpret()
    #dictionary.append(exit)
    push(exit)
    comma()

def compile_word():
    print('IN COMPILE WORD')
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


"""def dictionary[2]func(): #this is what dictionary[2] would do in forth?!
    print('IN dictionary[2] FUNC')
    push('dictionary[2]')
    find()

def get_dictionary[2]():
    push('dictionary[2]')
    find()

def set_dictionary[2]():
    push('dictionary[2]')
    find()
    pop()
    push(1)
    add()
    swap()
    store()
"""
def doliteral():
    print('\n\nin doliteral, index and index2 and dictionary[2] : ', index, index2, dictionary[2])
    print('will push: ', (dictionary[index2+1]))
    push(int(dictionary[index2+1]))
    #global dictionary[2]
    dictionary[2] = dictionary[2] + 1
    print_stack()
    next_word()

def literal():
    print('IN LITERAL')
    x = pop()
    dictionary.append(doliteral)
    dictionary.append(x)


def if_():
    print('IN IF')
    dictionary.append(Qbranch)
    dictionary.append(None)
    push(len(dictionary)-1) ##### CHECK THIS

def else_():
    print('IN ELSE')
    dictionary.append(branch)
    #print('in else')
    #print_dictionary()
    dictionary.append(None)
    push(len(dictionary)-1)
    #print(';len dict : ', len(dictionary))
    #push(len(dictionary)-2) ##### CHECK THIS

def Qbranch():
    #global dictionary[2]
    dictionary[2] = dictionary[2] + 1
    x = pop()
    push_RS(x)
    print('in qbranch') #, PC +1, x :', PC, x)
    if x != 0: #true - carry out first block
        print('TRUE')
        dictionary[2] = dictionary[2] + 1
        push(dictionary[2])
        execute()
    """else:
        print('FALSE')
        PC = dictionary[PC]
        push(PC)
        execute()"""

def branch():
    #global PC
    print('in branch')#, PC is', PC)
    x = pop_RS()
    if x == 0:
        print('FALSE')
        dictionary[2] = dictionary[2] + 2
        push(dictionary[2])
        execute()
    else:
        print('TRUE')
        dictionary[2] = dictionary[dictionary[2]+1]
        push(dictionary[2])
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
#add_word('PC', 0, variable, None)
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

input_stream = ": TEST 8 = IF 7 DUP ELSE 100 * THEN ; 5 8 TEST "
#input_stream = ": TEST IF 7 DUP ELSE 100 * THEN ; 5 1 TEST "
#input_stream = ": TEST IF 7 ELSE 100 THEN ; 1 TEST "
#input_stream = ": TWICE DUP + DUP ; : SQUARED DUP * ; : CUBED DUP SQUARED * ; 2 CUBED 3 SQUARED 5 TWICE .S "
quit()
print_dictionary
