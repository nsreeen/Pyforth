import sys, io
from contextlib import redirect_stdout

################### PARAM STACK ###################
stack = [] # using stack[-1] instead of a stack pointer

def PUSH(item):
    stack.append(item)

def POP():
    tos = stack.pop()
    return tos

################### RETURN stack ###################
Rstack = []

def RPUSH(item):
    Rstack.append(item)

def RPOP():
    tos = Rstack.pop()
    return tos

def RCLEAR():
    Rstack = []

################### Dictionary ###################
word_trace = [] #for debugging
STATE = 0 # 0 means interpret mode

LATEST = None
PC = None
W = None # 'working register'

def HERE():
    PUSH(len(dictionary) - 1)

def incrementLATEST():
    global LATEST
    HERE()
    print('HERE is ', stack[0])
    LATEST = POP()

def update_PC(new_PC):
    global PC
    PC = new_PC

def update_W(new_W):
    global W
    W = new_W

dictionary = []

class WordHeader():
    def __init__(self, name, link_address, code_pointer, immediate_flag=0):
        self.name = name
        self.immediate_flag = immediate_flag
        self.link_address = link_address
        self.code_pointer = code_pointer


#####################  ADDING TO DICTIONARY  and INPUT STREAM ##################
def COMMA():
    dictionary.append(POP())

def _COMMA(x):
    dictionary.append(x)

def CREATE():
    newWH = WordHeader(None, LATEST, ENTER)
    PUSH(newWH)
    COMMA()
    incrementLATEST()
    print('in CREATE, dictionary[LATEST].name = ', dictionary[LATEST].name)

def FIND():
    word = POP()
    current = LATEST
    while current != None: # None means we are at the first word in the dictionary
        if dictionary[current].name == word:
            PUSH(current)
            if dictionary[current].immediate_flag == 1:
                PUSH(-1)
            else:
                PUSH(1)
            return
        current = dictionary[current].link_address
    PUSH(word)
    PUSH(0)

def ACCEPT():
    global input_stream
    input_stream = input_stream.split()

def WORD():
    global input_stream
    print('in WORD, new word is ', input_stream[0])
    PUSH(input_stream[0])
    input_stream = input_stream[1:]

################### INTERPRETING AND COMPILING ##############################

def QUIT():
    RCLEAR()
    ACCEPT()
    while input_stream:
        if STATE:
            COMPILE()
        else:
            INTERPRET()

def INTERPRET():
    WORD()
    FIND()
    found = POP()
    if found == 1 or found is -1: # word was found, execute in interpret mode regardless of immediate flag
        EXECUTE()
    else:
        NUMBER()

def NUMBER():
    number = POP()
    PUSH(int(number))

def EXECUTE():
    update_W(POP())
    dictionary[W].code_pointer()

def set_interpret():
    global STATE
    STATE = 0

def set_compile():
    global STATE
    STATE = 1

def COLON():
    CREATE()
    set_compile()

def SEMICOLON():
    PUSH(EXIT)
    COMMA()
    set_interpret()

def COMPILE():
    WORD()
    print(dictionary[LATEST].name)
    if dictionary[LATEST].name == None:
        dictionary[LATEST].name = POP()
        return
    FIND()
    flag = POP()
    if flag == -1: # word has an immediate flag
        EXECUTE()
    elif flag == 1: # no immediate flag, word should be compiled
        COMMA()
    else:
        NUMBER()
        LITERAL() # word isn't found, it is a number

def LITERAL():
    _COMMA(DOLITERAL)
    _COMMA(POP())

def DOLITERAL():
    print('in do lit, will push ', dictionary[PC], ' onto stack')
    PUSH(dictionary[PC])
    update_PC(PC+1)
    print('updated PC to ', PC)
    NEXT()

################### THREADING ##############################

def EXIT():
    print('in exit, PC is ', PC)
    update_PC(RPOP()) # set PC to top of return stack
    if PC != None: # if we are returning to a composite word thread
        NEXT() # next word takes us to the next word in the composite word thread

def ENTER():
    print('in enter, PC is ', PC , ' W is ', W)
    RPUSH(PC) # push PC to return stack so we can return to it
    update_PC(W+1) # set PC to current index/ address in the dictionary
    NEXT()

def NEXT():
    print('in NEXT, PC is ', PC, ' W is ', W)
    if PC != None:
        update_W(PC)
        update_PC(PC + 1)
        JUMP()

def JUMP():
    # if we are following a thread, W has to follow
    if isinstance(dictionary[W], int):
        update_W(dictionary[W])

    # if it's a word header we have to execute the code pointer
    if isinstance(dictionary[W], WordHeader):
        dictionary[W].code_pointer()
    else:
        dictionary[W]()

######################## BRANCHING ######################
def IF():
    _COMMA(QBRANCH)
    _COMMA(None)
    HERE()

def ELSE():
    _COMMA(BRANCH)
    _COMMA(None)
    HERE()

    PUSH(1)
    ADD() # now we should have prev cell and current +1
    printS() # check

    # since need to implement SWAP, TUCK, and STORE
    a = POP()
    b = POP()
    diff = a - b
    addr = b
    dictionary[addr] = diff

    HERE()

def THEN():
    HERE()

    PUSH(1)
    ADD() # now we should have prev cell and current +1
    printS() # check

    # since need to implement SWAP, TUCK, and STORE
    a = POP()
    b = POP()
    diff = a - b
    addr = b
    dictionary[addr] = diff

def QBRANCH():
    print('in QBRANCH, PC is ', PC)
    printS()
    flag = POP()
    if flag == 0: # condition is FALSE
        update_PC(PC+dictionary[PC])
        print('PC changed to : ', PC, ' which has ', dictionary[PC])
    else: # flag != 0, condition is TRUE
        update_PC(PC+1) # avoid cell with number in it
        print('PC changed to : ', PC, ' which has ', dictionary[PC])
    NEXT()

def BRANCH():
    print('in BRANCH')
    printS()
    update_PC(PC+dictionary[PC])
    NEXT()


################### NATIVE FUNCTIONS ###################

def DUP():
    top = stack[-1]
    PUSH(top)
    NEXT()

def MUL():
    a = POP()
    b = POP()
    print('in MUL, a and b are: ', a, b)
    PUSH(a * b)
    NEXT()

def ADD():
    a = POP()
    b = POP()
    PUSH(a + b)
    NEXT()

def EQUALS():
    a = POP()
    b = POP()
    if a == b:
        PUSH(1)
    else:
        PUSH(0)
    NEXT()

#################### PRINTING AND DEBUGGING ###################
def printS():
    #global output
    stri = ""
    stri = stri + "<" + str(len(stack)) + "> "
    for item in stack:
        stri = stri + str(item) + " "
    #output += stri
    print(stri)

def printD(last_section_only=0):
    if last_section_only == 1:
        start = len(dictionary) - 20
    else:
        start = 0
    for i in range(start, len(dictionary)):
        if isinstance(dictionary[i], WordHeader):
            try:
                cell = str(dictionary[i].name)
            except:
                cell = str(dictionary[i])
        else:
            cell = dictionary[i]
        x = ""
        #if cell != 0 and isinstance(cell, int):
        #    x = "    | " + str(dictionary[cell])
        print(i, cell, x)


################ ADD NATIVE WORDS TO DICTIONARY ####################

words_to_add_to_dictionary = [('.S', printS), ('DUP', DUP), ('*', MUL),
('+', ADD), (':', COLON, 1), (';', SEMICOLON, 1), ('.D', printD), ('=', EQUALS),
('IF', IF, 1), ('ELSE', ELSE, 1), ('THEN', THEN, 1)]

for word in words_to_add_to_dictionary:
    if len(word) > 2:
        imm_flag = word[2]
    else:
        imm_flag = 0
    newWH = WordHeader(word[0], LATEST, word[1], imm_flag)
    _COMMA(newWH)
    incrementLATEST()

#########################################


if __name__ == "__main__":
    input_stream = " : ZERO? 0 = IF 1 ELSE 0 THEN ; 1 .S ZERO? .S "
    QUIT()
