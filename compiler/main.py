import sys
import PLoxVM

def repl():
    while True:
        print(">")
        line=input()
        if len(line)==0:
            break
        PLoxVM.interpret(line)  

def runfile(filepath):
    with open(filepath, 'r') as file:
        source = file.read()
        result=PLoxVM.interpret(source)
        if result==PLoxVM.InterpretResult.INTERPRET_COMPILE_ERROR:
            exit(65)
        elif result==PLoxVM.InterpretResult.INTERPRET_RUNTIME_ERROR:
            exit(70)


if __name__ == "__main__":
    args=sys.argv
    PLoxVM.initVM()
    if len(args)==2:
        runfile(args[1]) 
    elif len(args)==1:
        repl()
    else:
        print("[Usage] main.py filename")
        exit(64)   
    PLoxVM.freeVM()
    
    
    
    