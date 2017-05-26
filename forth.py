# PARAM STACK
stack = []
SP = None

def print_stack():
    print('\n Printing the stack: ')
    for slot in reversed(stack):
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

dictionary = []

PC = None

here = None

def add_word(name,immediate_flag,  code_pointer, data_field):
    global here
    #new_cell = {
    #    'name': name,
    #    'link_address': previous,
    #    'code_pointer': code_pointer,
    #    'data_field': word_list
    #}
    dictionary.append(name)
    dictionary.append(here)
    placer_for_here = len(dictionary) - 1
    if code_pointer != None: # there is a link, this is not a composite word
        dictionary.append(code_pointer)
        dictionary.append(next_word)

    else: # this is a composite word
        dictionary.append(enter)
        for word in data_field:
            push(word)
            print(' !!!!!!!! adding composite word list')
            print_stack()
            find()
            print_stack()
            pop()
            link = pop()
            dictionary.append(link)
        dictionary.append(exit)
    here = placer_for_here

def print_dictionary():
    for cell in dictionary:
        print(cell)

# NATIVE DICTIONARY FUNCTIONS
def dup():
    top = stack[SP]
    push(top)

def mul():
    a = pop()
    b = pop()
    result = a * b
    push(result)

def exit():
    """
    Moves the xt at the top of the RS to the PC
    ie exits the thread
    """
    pass

def enter():
    """
    Moves whatever is at the CP to the RS
    Moves ???? to the PC
    """
    global PC
    #if PC != None:
    push_RS(PC)
    # this only works while the dictionary doesnt have duplicates
    # find better way111! ctypes!?!?!
    current_index = dictionary.index(PC)
    PC = dictionary[current_index+1]

def next_word():
    """
    PC moves to next cell in dictionary
    """
    global PC
    print('<@> PC is ', PC)
    #current = PC
    current_index = dictionary.index(PC)
    PC = dictionary[current_index+1]
    #push(current)


def execute():
    """
    Moves what is on the top of the param stack to the working register?
    for now just execute it
    """
    tos = pop()
    #if tos == None: ##### index() gets the first instance it finds?!
    #PC = tos
    tos()

def word():
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
    print('\n in find, new_word is: ', new_word)
    current_link_index = here
    while current_link_index != None:
        #print(current_link_index) #9
        #print(dictionary[current_link_index]) #5
        current_name = dictionary[current_link_index-1]
        print('current_name:', current_name)
        if current_name.strip() == new_word.strip():
            print('FOUND')
            current_code_pointer = dictionary[current_link_index+1]
            push(current_code_pointer)
            push(1)
            return
        current_link_index = dictionary[current_link_index]
    push(new_word)
    push(0)

def number():
    string = pop()
    number = int(string)
    push(number)

def interpret():
    #print('\n before word')
    #print_stack()
    word()
    #print('\n after word')
    #pprint_stack()
    find()
    #print('\n after find')
    print_stack()
    #print('\n')
    tos = pop()
    if tos == 1:
        execute()
    else:
        number()

def quit():
    while len(input_stream):
        print('\n input_stream', input_stream)
        interpret()




# Add some words to dictionary
add_word('.S', 0, print_stack, [])
add_word('DUP', 0, dup, [])
add_word('*', 0, mul, [])
print_dictionary()
print('--------------------------------------------')
add_word('SQUARED', 0, None, ['DUP', '*'])






### TESTS
def test_stack():
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
    print('test the linked list')
    current = here
    print(current)
    while current != None:
        current = dictionary[current]
        print(current)

#test_stack()
#print_dictionary()
#print('test pc which should point to last thing added to dictionary')
#dictionary[here+1]()
#print_stack()
push(5)
print('\n interpreting stream : " SQUARED .S " ')
input_stream = " DUP * .S "
quit()
print_stack()
