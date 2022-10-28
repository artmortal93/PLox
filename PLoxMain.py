import sys
from PLoxDef import TokenType,Token
from PLox import PLox

if __name__ == "__main__":
    entrylist=sys.argv
    plox=PLox()
    if len(entrylist)>2:
        print("Usage: plox [script]")
        exit()
    elif len(entrylist)==2:
        plox.runFile(entrylist[1])
    elif len(entrylist)==1: #run in REPL
        plox.runPrompt()







    
