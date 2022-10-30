from PLoxScanner import Scanner
from PLoxDef import *
from PLoxParser import Parser
from PLoxInterpreter import PLoxInterpreter

class PLox(object):
    hadError=False
    hadRuntimeError=False
    def __init__(self):
        super().__init__()
        self.data=None
        self.interpreter=PLoxInterpreter()
        
        
    def runFile(self,filepath:str):
        with open(filepath, 'r') as file:
            self.data = file.read()
        self.run(self.data)
        if PLox.hadError:
            exit(65)
        if PLox.hadError:
            exit(70)
    
    def runPrompt(self):
        while True:
            print(">", end='')
            line=input()
            #print(len(line))
            if(len(line)==0):
                print("Leaving REPL Mode...")
                break
            self.run(line)
            PLox.hadError=False
    
    def run(self,source:str):
        scanner=Scanner(source)
        tokens=scanner.scanTokens()
        parser=Parser(tokens)
        expression=parser.parse()
        if PLox.hadError:
            return;
        self.interpreter.interpret(expression)
        for token in tokens:
            print(token)
        #printer=ASTPrinter()
        #print(printer.print(expression))
        
   
    @staticmethod
    def error(line:int,message:str):
        PLox.report(line,"",message)

    @staticmethod
    def tokenError(token:Token,message:str):
        if token.type==TokenType.EOF:
            PLox.report(token.line,"at end",message)
        else:
            PLox.report(token.line,"at '"+token.lexeme+"'",message)

    @staticmethod
    def runtimeError(error:RunTimeError):
        PLox.hadRuntimeError=True
        print(error.message+" [line"+str(error.token.line)+"]")

    @staticmethod
    def report(line:int,where:str,message:str):
        print("line {} error, {}:{}".format(line,where,message))
        hadError=True
