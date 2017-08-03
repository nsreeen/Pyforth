# The dictionary
The dictionary is a list, so each cell is an item in the list. Each Forth word is spread over 2+ cells/items.

Word headers are an object with attributes: name, immediate flag, link address.

Code pointers are in the cell after the header.  If there is a data field it is after the code pointer, with each word in the data field taking up it's own cell.

# Keeping track in Python
Use global variables for Forth keeping track variables HERE, LATEST, PC.  
To avoid ugly 'global''s everywhere, and make things clearer and easier to read, use dedicated functions to update these variables.

* HERE - end of dictionary
In Python, we can just do len(dictionary), so no need for a dedicated variable.  Instead HERE is a function which pushes the length - 1

* LATEST - last word added
Latest points to the last word added to the dictionary, in this implementation it points to a word header object
update_LATEST(new_latest) t update it

* PC
Will explain this below with threading.
Update_PC(new_PC) updates it

* index
Can't access memory address in Python so global index variable to keep track of where we are in the dictionary.  This is important later for threading

* STATE
1 -> compile, 0 -> interpret
set_compile() and set_interpret() change it

# Finding words
find() takes a word from the top of the stack and pushes two things to the stack: the word or it's index in the dictionary, and a number

find() compares the word it got off the stack to word names in the dictionary until it finds a match or runs out of words to compare to. It starts at LATEST - the last word added - as the current word header object to check.  

The name attribute of the current header is checked, and if it doesn't match the link_address attribute is used to get to the next word header to check.

If it matches the current index is pushed to the stack.

If its not found the word itself is pushed to the stack, because if it's not in the dictionary we might want to do something else with it.  It might be a number we want to push to the stack.

After pushing either an index/ address to the words code or the word itself, it pushes a number:
If it's found, either -1 or 1 (based on the word's immediate flag)
If it isn't found, 0.

# get_word() and the input stream

Originally I parsed the input stream in the Forth way: I had a word() function that took one character at a time from the input stream, and either added it to the new word or returned the new word if the character was a space.  This seemed messy and unnecessarily complex when writing a Python implementation, so I decided to do it in a neater way.  

In quit(), the input stream is split into a list.  Each new line of input calls quit(), so each time it is called it makes a new list.

get_word() takes the item at the start of the input stream list as a new word, and removes it from the list.


# interpreting a word

interpret_word does the following:

* calls get_words(), which leaves the next word from the input stream on the stack

* calls find, which leave two things on the stack.  interpret_word() pops the top of the stack which is a number

- if it's 1 or -1, we know the top of the stack is now an address in the dictionary (well an index in a list) and execute() is called

- if it's 0, we know the top of the stack is now the word we got earlier and that it wasn't found in the dictionary. We assume it's a number and call number() which will make it an int and push it to the stack.  ** at the moment we are not dealing with a non-number that isn't in the dictionary eg a mistyped word




# execute
Execute pops an index from the stack.  That index points to a cell that might contain:
* a function pointer - in which case we want to execute the contents
* a WordHeader object - in which case we want to execute the contents of the cell after
* an index to another cell - in which we want to get to the contents of that other cell
* an index which points to another cell, which points to another cell <- avoid this!

# Compiling new words

# Threading
(how composite words are executed, in case they are layered)
index: When a word is executed, index is updated with that words index.  

# IF ELSE THEN

IF:
appends Qbranch
appends an empty cell (containing None)
and pushes the current index to the stack (by calling HERE())

ELSE:
appends branch
appends an empty cell
pushes the current index to the stack



# DO LOOP
