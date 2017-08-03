# Pyforth

A mini Forth implemented in Python.  Available as a REPL for the terminal and in a web app.



## Usage

To run the REPL:
1) You must have python 3.5 installed
2) Save a copy of this directory locally (type ```git clone https://github.com/Nasreen123/Pyforth.git``` in your terminal)
3) Type ```python pyforth/pyforth.py``` from the root of the directory (don't go into a subfolder)

To interpret a Forth file and run the REPL:
1) Save the file in your copy of this directory
2) Type ```python pyforth/pyforth.py <filename>```



## Web app

https://pyforth.herokuapp.com/



## Builtin words implemented so far:
```
.S DUP * + - = < >  
OVER SWAP ROT DROP NIP TUCK 2DUP MOD
: ; ! @  ,
>R R> R@ R0
IF ELSE THEN DO LOOP I J
.D // prints the dictionary
```
