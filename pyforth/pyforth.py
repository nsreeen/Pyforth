import sys

input_stream = ""
output = ""

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
    Rstack.clear()

def toR(): # >R ( x - R:x )
    x = POP()
    RPUSH(x)

def fromR(): # R> ( R:x - x )
    x = RPOP()
    PUSH(x)

def Rtop(): # ( R:x - R:x x )
    x = RPOP()
    PUSH(x)
    RPUSH(x)

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

def STORE(): # ( contents address -- )
    addr = POP()
    content = POP()
    dictionary[addr] = content

def FETCH(): # ( address - contents )
    addr = POP()
    PUSH(dictionary[address])

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
    PUSH(dictionary[PC])
    update_PC(PC+1)
    NEXT()

################### THREADING ##############################

def EXIT():
    update_PC(RPOP()) # set PC to top of return stack
    if PC != None: # if we are returning to a composite word thread
        NEXT() # next word takes us to the next word in the composite word thread

def ENTER():
    RPUSH(PC) # push PC to return stack so we can return to it
    update_PC(W+1) # set PC to current index/ address in the dictionary
    NEXT()

def NEXT():
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
def ADD1():
    PUSH(1)
    ADD()

def OFFSET():
    SUB()

def IF():
    _COMMA(QBRANCH)
    _COMMA(None)
    HERE()

def RESOLVE():
    ADD1() # now we should have prev cell and current +1
    OVER()
    OFFSET()
    SWAP()
    STORE()

def ELSE():
    _COMMA(BRANCH)
    _COMMA(None)
    HERE()
    RESOLVE()
    HERE()

def THEN():
    HERE()
    RESOLVE()

def QBRANCH():
    flag = POP()
    if flag == 0: # condition is FALSE
        update_PC(PC+dictionary[PC])
    else: # flag != 0, condition is TRUE
        update_PC(PC+1) # avoid cell with number in it
    NEXT()

def BRANCH():
    update_PC(PC+dictionary[PC])
    NEXT()

def DO():
    I = POP()
    J = POP()
    addr = PC - 1
    RPUSH(J)
    RPUSH(I)
    RPUSH(addr)
    NEXT()

def LOOP():
    addr = RPOP()
    I = RPOP()
    J = RPOP()
    I = I + 1
    if I != J:
        update_PC(addr)
        PUSH(J)
        PUSH(I)
    NEXT()

def I():
    i = Rstack[-2]
    PUSH(i)
    NEXT()

def J():
    j = Rstack[-3]
    PUSH(j)
    NEXT()


################### STACK  FUNCTIONS ###################

def DUP():
    top = stack[-1]
    PUSH(top)
    NEXT()

def SWAP():
    a = POP() #top
    b = POP() #second
    PUSH(a)
    PUSH(b)

def OVER():
    top = POP()
    second = POP()
    PUSH(second)
    PUSH(top)
    PUSH(second)

def MUL():
    a = POP()
    b = POP()
    PUSH( a * b )
    NEXT()

def ADD():
    a = POP()
    b = POP()
    PUSH( a + b )
    NEXT()

def SUB():
    a = POP()
    b = POP()
    PUSH( b - a )
    NEXT()

def EQUALS():
    a = POP()
    b = POP()
    if a == b:
        PUSH(1)
    else:
        PUSH(0)
    NEXT()

def less_than(): # ( a b - bool )  bool = a<b
    b = POP()
    a = POP()
    if a < b:
        PUSH(1)
    else:
        PUSH(0)
    NEXT()

def greater_than(): # ( a b - bool )  bool = a>b
    b = POP()
    a = POP()
    if a > b:
        PUSH(1)
    else:
        PUSH(0)
    NEXT()

def ROT(): # ( c b a - b a c )
    a = POP()
    b = POP()
    c = POP()
    PUSH(b)
    PUSH(a)
    PUSH(c)

def DROP(): # ( a - )
    POP()

def NIP(): # ( a b - b )
    b = POP()
    POP()
    PUSH(b)

def TUCK(): # ( a b - b a b )
    b = POP()
    a = POP()
    PUSH(b)
    PUSH(a)
    PUSH(b)

def TWODUP(): # ( a b - a b a b )
    b = POP()
    a = POP()
    PUSH(a)
    PUSH(b)
    PUSH(a)
    PUSH(b)

def MOD(): # ( a b - a%b )
    b = POP()
    a = POP()
    PUSH(a%b)
#################### PRINTING AND DEBUGGING ###################
def printS():
    stri = ""
    stri = stri + "<" + str(len(stack)) + "> "
    for item in stack:
        stri = stri + str(item) + " "
    add_output(stri)
    NEXT()

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


################ ADD BUILTIN WORDS TO DICTIONARY ####################

words_to_add_to_dictionary = [('.S', printS), ('DUP', DUP), ('*', MUL),
('+', ADD), ('-', SUB), (':', COLON, 1), (';', SEMICOLON, 1), ('.D', printD),
('=', EQUALS), ('IF', IF, 1), ('ELSE', ELSE, 1), ('THEN', THEN, 1), ('!', STORE),
('@', FETCH), ('OVER', OVER), ('SWAP', SWAP), ('ROT', ROT), ('DROP', DROP),
('NIP', NIP), ('TUCK', TUCK), ('2DUP', TWODUP), ('MOD', MOD), ('R0', RCLEAR),
('>R', toR), ('R>', fromR), ('R@', Rtop), ('.S', printS), ('DO', DO),
('LOOP', LOOP), ('I', I), ('J', J), ('<', less_than),
('>', greater_than)]

for word in words_to_add_to_dictionary:
    if len(word) > 2:
        imm_flag = word[2]
    else:
        imm_flag = 0
    newWH = WordHeader(word[0], LATEST, word[1], imm_flag)
    _COMMA(newWH)
    incrementLATEST()

#########################################

def add_output(new_output):
    global output
    output = output + new_output

def set_input_stream(new_input):
    global input_stream
    input_stream = new_input

def get_file_text(filename):
    filetext = open(filename, 'r')
    filetext_joined = " ".join(filetext)
    filetext.close()
    return filetext_joined

def reset_output():
    global output
    output = ""

def reset_stacks():
    global stack
    stack = []
    global Rstack
    Rstack = []


def webrepl(input_lines):
    output_lines = []
    reset_stacks()
    for line in input_lines:
        set_input_stream(line)
        QUIT()
        output_lines.append(output)
        reset_output()
    return output_lines

if __name__ == "__main__":

    if len(sys.argv) > 1:
        filetext = get_file_text(sys.argv[1])
        set_input_stream(filetext)

    running = True
    while running:
        if input_stream:
            output = ""
            QUIT()
            print("".join(output))
        input_stream = input()
