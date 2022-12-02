PLox Interpreter for Lox Language in Book 'Crafting Interpreters',written in python.

This Repo contain two complete full parts, a tree walk interepreter for first part of the book 
and a bytecode VM stack compiler for the second part of the book, both are runnable and complete!

The purpose is Code to learn,JLox is good,but CLox are somehow trouble some, expesically CLox has many macro
and pointer tricks in C,it make you feel bad because basically you have no choice but just copy and paste when you are reading the second part of the book when try to follow.
I try to simplify in py get rid of those flying global/macro s**t and here's the outcome.

Both two language interpreter/compiler have a bootstrap file call code.plox so you could try to run in python <br />
Usage example: <br />
For execute a file in interpreter: <br />
cd /interpreter <br />
python3 PLoxMain.py code.plox <br />
For execute a file in compiler: <br />
cd /compiler <br />
python3 main.py code.plox <br />

