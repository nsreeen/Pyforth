

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
    print('LATEST is ', LATEST)

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
    print('\n IN EXECUTE. W is ', W, ' points to WH with CP: ', dictionary[W].code_pointer)
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
    print('in exit, PC is NOW', PC)
    if PC != None: # if we are returning to a composite word thread
        NEXT() # next word takes us to the next word in the composite word thread

def ENTER():
    print('in enter, PC is ', PC , ' W is ', W)
    RPUSH(PC) # push PC to return stack so we can return to it
    update_PC(W+1) # set PC to current index/ address in the dictionary
    NEXT()

def NEXT():
    print('\n in NEXT, PC is ', PC, ' W is ', W)
    if PC != None:
        update_W(PC)
        update_PC(PC + 1)
        print('\n PC not None so now: PC is ', PC, ' W is ', W, ' calling jump')
        JUMP()

def JUMP():
    # if we are following a thread, W has to follow
    if isinstance(dictionary[W], int):
        update_W(dictionary[W])

    # if it's a word header we have to execute the code pointer
    if isinstance(dictionary[W], WordHeader):
        print('in JUMP, will execute: ', dictionary[W].code_pointer)
        dictionary[W].code_pointer()
    else:
        print('in JUMP, will execute: ', dictionary[W])
        dictionary[W]()

def BYE():
    if running:
        global running
        running = False

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
    print('in QBRANCH, PC is ', PC)
    print('stack: ', stack)
    flag = POP()
    print('flag: ', flag)
    if flag == 0: # condition is FALSE
        update_PC(PC+dictionary[PC])
        print('PC changed to : ', PC, ' which has ', dictionary[PC])
    else: # flag != 0, condition is TRUE
        update_PC(PC+1) # avoid cell with number in it
        print('PC changed to : ', PC, ' which has ', dictionary[PC])
    print('end of QBRANCH, PC now: ', PC)
    NEXT()

def BRANCH():
    print('in BRANCH, PC and W are: ', PC, W)
    update_PC(PC+dictionary[PC])
    print('PC is now: ', PC)
    NEXT()

def DO():
    print('\nstart of do, PC and W are: ', PC, W)
    I = POP()
    J = POP()
    addr = PC - 1
    print('in DO, I J and addr are: ', I, J, addr)
    RPUSH(J)
    RPUSH(I)
    RPUSH(addr)
    NEXT()

def LOOP():
    print('\nstart of loop, PC and W are: ', PC, W)
    addr = RPOP()
    I = RPOP()
    J = RPOP()
    I = I + 1
    print('in LOOP, I J and addr are: ', I, J, addr)
    if I != J:
        print('I and J are not equal')
        update_PC(addr)
        PUSH(J)
        PUSH(I)
    print('PC and W are: ', PC, W)
    NEXT()

def I():
    print('in I')
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
    print('in MUL, a and b are: ', a, b)
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


################ ADD NATIVE WORDS TO DICTIONARY ####################

words_to_add_to_dictionary = [('.S', printS), ('DUP', DUP), ('*', MUL),
('+', ADD), ('-', SUB), (':', COLON, 1), (';', SEMICOLON, 1), ('.D', printD),
('=', EQUALS), ('IF', IF, 1), ('ELSE', ELSE, 1), ('THEN', THEN, 1), ('!', STORE),
('@', FETCH), ('OVER', OVER), ('SWAP', SWAP), ('ROT', ROT), ('DROP', DROP),
('NIP', NIP), ('TUCK', TUCK), ('2DUP', TWODUP), ('MOD', MOD), ('R0', RCLEAR),
('>R', toR), ('R>', fromR), ('R@', Rtop), ('.S', printS), ('DO', DO),
('LOOP', LOOP), ('I', I), ('J', J), ('BYE', BYE), ('<', less_than),
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

def webrepl(input_lines, consistent_dictionary, consistent_stack):
    set_input_stream(input_lines)
    QUIT()
    return dictionary, stack, output

if __name__ == "__main__":
    input_stream = " 1 2 3 >R >R R> .S "

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
