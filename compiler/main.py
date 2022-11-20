import sys
from chunk import *
from PLoxVM import *
from debug import *

def repl():
    while True:
        print(">")
        line=input()
        if len(line)==0:
            break
        interpret(line)  

def runfile(filepath):
    with open(filepath, 'r') as file:
        source = file.read()
        result=interpret(source)
        if result==InterpretResult.INTERPRET_COMPILE_ERROR:
            exit(65)
        elif result==InterpretResult.INTERPRET_RUNTIME_ERROR:
            exit(70)


if __name__ == "__main__":
    args=sys.argv
    initVM()
    if len(args)==2:
        runfile(args[1]) 
    elif len(args)==1:
        repl()
    else:
        print("[Usage] main.py filename")
        exit(64)   
    freeVM()
    
    
    
    