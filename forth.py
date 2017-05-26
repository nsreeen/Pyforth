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

dictionary = []

index = None # way to keep track of the 'address' index - work around because using python

PC = None

here = None

def add_word(name, immediate_flag, code_pointer, data_field):
    print('adding name to dict ', name)
    global here
    dictionary.append(name)
    dictionary.append(here)
    placer_for_here = len(dictionary) - 1

    if code_pointer != None: # there is a link, this is not a composite word
        dictionary.append(code_pointer)

    else: # this is a composite word
        dictionary.append(enter)
        for word in data_field:
            push(word)
            find()
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

def exit():
    global PC
    PC = pop_RS()
    if PC != None:
        next_word()


def enter():
    print('#####in enter, PC  and index: ', PC, index, 'type pc', type(PC))
    global PC
    push_RS(PC)
    PC = index
    print('#####in enter, PC  and index: ', PC, index, 'type pc', type(PC))
    next_word()



def next_word():
    global PC
    PC = PC + 1
    push(PC)
    execute()


def execute():
    tos = pop()
    point_to = None

    if not isinstance(dictionary[tos], int):
        point_to = tos
    else:
        point_to = dictionary[tos]

    global index
    index = point_to

    print('\n\n0000000000000000in execute, tos is ', tos)
    print_stack()

    dictionary[point_to]()


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
    current_link_index = here
    while current_link_index != None:
        current_name = dictionary[current_link_index-1]
        if current_name.strip() == new_word.strip():
            push(current_link_index + 1)
            push(1)
            return
        current_link_index = dictionary[current_link_index]
    push(new_word)
    push(0)

def number():
    string = pop()
    number = int(string)
    push(number)

def interpret-word():
    word()
    find()
    tos = pop()
    if tos == 1:
        execute()
    else:
        number()

def quit():
    global return_stack
    return_stack = []
    while len(input_stream):
        interpret-word()




# Add some words to dictionary
add_word('.S', 0, print_stack, [])
add_word('DUP', 0, dup, [])
add_word('*', 0, mul, [])
add_word('+', 0, add, [])
print('--------------------------------------------')
print_dictionary()
print('--------------------------------------------')
add_word('SQUARED', 0, None, ['DUP', '*'])
print('--------------------------------------------')
print_dictionary()
print('--------------------------------------------')

add_word('CUBED', 0, None, ['DUP', 'SQUARED', '*'])
add_word('TEST', 0, None, ['DUP', 'CUBED', '+'])
print('--------------------------------------------')
print_dictionary()
print('--------------------------------------------')



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


input_stream = " 10 TEST .S "
quit()
