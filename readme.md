PLOX Interpreter for Lox Language in Book 'Crafting Interpreters',written in python.

This Repo contain two complete full parts, a tree walk interepreter for first part of the book 
and a bytecode VM stack compiler for the second part of the book, both are runnable and complete!

The purpose is Code to learn,JLOX is good,but CLOX are somehow trouble some, expesically clox has many macro
and pointer tricks in C,it make you feel bad because basically you have no choice but just copy and paste when you are read the second part of the book and try to follow.
I try to simplify in py get rid of those flying global/macro s**t and here's the outcome.

Both two language interpreter/compiler have a bootstrap file call code.plox so you could try to run in python
Usage example:
For execute a file in interpreter:
cd /interpreter
python3 PLoxMain.py code.plox
For execute a file in compiler:
cd /compiler
python3 main.py code.plox

