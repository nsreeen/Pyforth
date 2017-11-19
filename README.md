

A mini Forth implemented in Python. To visualize the stack go to: https://pyforth.herokuapp.com/visualizer


<br>
# terminal tool usage:

To run the REPL:
1) You must have python 3.5 installed
2) Save a copy of this directory locally (type ```git clone https://github.com/Nasreen123/Pyforth.git``` in your terminal)
3) Type ```python pyforth/pyforth.py``` from the root of the directory (don't go into a subfolder)

To interpret a Forth file and run the REPL:
1) Save the file in your copy of this directory
2) Type ```python pyforth/pyforth.py <filename>```




<br>
# builtin words implemented so far:
<br> `.S` `DUP` `*` `+` `-` `=` `<` `>`
<br> `OVER` `SWAP` `ROT` `DROP` `NIP` `TUCK` `2DUP` `MOD`
<br> `:` `;` `!` `@` `,`
<br>> `R` `R>` `R@` `R0`
<br> `IF` `ELSE` `THEN` `DO` `LOOP` `I` `J`
<br> `.D` // prints the dictionary, only works in the terminal
