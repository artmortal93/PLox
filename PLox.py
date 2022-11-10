from PLoxScanner import Scanner
from PLoxDef import *
from PLoxParser import Parser
from PLoxResolver import Resolver
from PLoxInterpreter import Interpreter

class PLox(object):
    hadError=False
    def __init__(self):
        super().__init__()
        self.data=None
        self.interpreter=Interpreter()
        
        
    def runFile(self,filepath:str):
        with open(filepath, 'r') as file:
            self.data = file.read()
        self.run(self.data)
        if PLox.hadError:
            exit(65)
    
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
        statments=parser.parse()
        resolver=Resolver(self.interpreter)
        if PLox.hadError:
            return;
        resolver.resolve(statments)
        self.interpreter.interpret(statments)
       
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
        PLox.hadError=True
        print(error.message+" [line"+str(error.token.line)+"]")

    @staticmethod
    def report(line:int,where:str,message:str):
        print("line {} error, {}:{}".format(line,where,message))
        PLox.hadError=True
