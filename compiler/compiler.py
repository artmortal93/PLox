from scanner import *
from debug import *
from chunk import *
from value import *
import PLoxVM
import os 

class ParseRule:
    def __init__(self,prefix,infix,precedence) -> None:
        self.prefix=prefix
        self.infix=infix
        self.precedence=precedence
        
#from lowest precedence to higher precendence        
class Precedence(IntEnum):
    PREC_NONE=0,
    PREC_ASSIGNMENT=1,
    PREC_OR=2, 
    PREC_AND=3, 
    PREC_EQUALITY=4, 
    PREC_COMPARISON=5, 
    PREC_TERM=6, 
    PREC_FACTOR=7, 
    PREC_UNARY=8, 
    PREC_CALL=9, 
    PREC_PRIMARY=10
    
class FunctionType(Enum):
    TYPE_FUNCTION=0
    TYPE_SCRIPT=1
    
class Local:
    def __init__(self) -> None:
        self.name=Token()
        self.depth=0
        
class Compiler:
    def __init__(self) -> None:
        self.function=None
        self.type=None
        self.locals=[None]*256
        self.localCount=0
        self.scopeDepth=0
        self.enclosing=None #it's fatherfunction scope
        
class Parser:
    def __init__(self) -> None:
        self.current=Token() #Token type
        self.previous=Token() #Token type
        self.hadError=False
        self.panicMode=False
        
#the starting point of recursive parsing   
#hint: at the start you get a current token and  null previous token
def expression():
    parsePrecedence(Precedence.PREC_ASSIGNMENT)
    
def declaration():
    global parser
    if match(TokenType.VAR):
        varDeclaration()
    elif match(TokenType.FUN):
        funDeclaration()
    else:
        statement()
    if parser.panicMode:
        synchronize()
        
def funDeclaration():
    global_idx=parseVariable("Expect function name")
    markInitialized()
    function(FunctionType.TYPE_FUNCTION)
    defineVariable(global_idx)
    
def function(type:FunctionType):
    #create a local compiler
    global current
    localCompiler=Compiler()
    initCompiler(localCompiler,type) #init and make it current compiler(chunk)
    beginScope()# a new compiler comes with new local, but all function variable are relative so you dont want
    #to end the scope because all variable should be local in a function
    consume(TokenType.LEFT_PAREN,"Expect ( after function name")
    if not check(TokenType.RIGHT_PAREN):
        while True:
            current.function.arity+=1
            if current.function.arity>255:
                errorAtCurrent("Cant have more than 255 parameters")
            paramConstant=parseVariable("Expect parameter name")
            defineVariable(paramConstant)
            if not match(TokenType.COMMA):
                break
    consume(TokenType.RIGHT_PAREN,"Expect ) after function name")
    consume(TokenType.LEFT_BRACE,"Expect { before function body")
    block()
    function=endCompiler() #pop out the function current compiler hold
    #endScope() #why missing
    emitBytes(OpCode.OP_CONSTANT,makeConstant(OBJ_VAL(function)))
        
def varDeclaration():
    #if we are in block that scope>0 parse and define do nothing
    global_idx=parseVariable("Expect variable name")
    if match(TokenType.EQUAL):
        expression()#only keep variable in stack
    else:
        emitByte(OpCode.OP_NIL)
    consume(TokenType.SEMICOLON,"expect ';' after value in value declaration.")
    defineVariable(global_idx)
    
    
def parseVariable(errorMessage):
    global current
    consume(TokenType.IDENTIFER,errorMessage)
    #this only works on local, global do not work
    declareVariable()
    if current.scopeDepth>0:
        return 0 #we dont need go into global variable if is in block
    return identifierConstant(parser.previous)

def declareVariable():
    global current
    global parser 
    if current.scopeDepth==0:
        return 
    name=parser.previous
    #detect rename var error
    for i in reversed(range(0,current.localCount)):
        local=current.locals[i]
        if local.depth!=-1 and local.depth<current.scopeDepth:
            break 
        if identifierEqual(name,local.name):
            error("Already define variable with name in current scope")
    addLocal(name)
    
def addLocal(name:Token):
    global current
    local=Local()
    local.name=name
    local.depth=-1
    current.locals[current.localCount]=local
    current.localCount+=1

def identifierConstant(name:Token):
    global parser
    global globalSource
    varName=globalSource[name.start:name.start+name.length]
    return makeConstant(OBJ_VAL(copyString(varName,name.length)))

def identifierEqual(a:Token,b:Token):
    global globalSource
    if a.length != b.length:
        return False
    aStr=globalSource[a.start:a.start+a.length]
    bStr=globalSource[b.start:b.start+b.length]
    return aStr==bStr

def defineVariable(global_idx):
    global current
    if current.scopeDepth>0: #we dont define global
        markInitialized()
        return  
    emitBytes(OpCode.OP_DEFINE_GLOBAL,global_idx)
    
def markInitialized():
    global current
    if current.scopeDepth==0:
        return 
    current.locals[current.localCount-1].depth=current.scopeDepth
    
#recieve a identifier        
def namedVariable(name:Token,canAssign:bool):
    global current
    getOp=0
    setOp=0
    #the stack and the locals are have same layout i runtime
    arg=resolveLocal(current,name)
    if arg!=-1:
        getOp=OpCode.OP_GET_LOCAL
        setOp=OpCode.OP_SET_LOCAL
    else:
        arg=identifierConstant(name)
        getOp=OpCode.OP_GET_GLOBAL
        setOp=OpCode.OP_SET_GLOBAL
    if match(TokenType.EQUAL) and canAssign:
        expression()
        emitBytes(setOp,arg)
    else:
        emitBytes(getOp,arg)

def resolveLocal(compiler:Compiler,name:Token):
    for i in reversed(range(0,compiler.localCount)):
        local=compiler.locals[i]
        if identifierEqual(name,local.name):
            if local.depth==-1:
                error("Cant not read local varaible in it's initalizer")
            return i 
    return -1
    
def statement():
    if match(TokenType.PRINT):
        printStatement()
    elif match(TokenType.IF):
        ifStatement()
    elif match(TokenType.LEFT_BRACE):
        beginScope()
        block()
        endScope()
    elif match(TokenType.WHILE):
        whileStatement()
    elif match(TokenType.RETURN):
        returnStatement()
    elif match(TokenType.FOR):
        forStatement()
    else:
        expressionStatement()
        
def printStatement():
    expression()
    consume(TokenType.SEMICOLON,"expect ';' after value. in print")
    emitByte(OpCode.OP_PRINT)
    
def expressionStatement():
    expression()
    consume(TokenType.SEMICOLON,"expect ';' after value. in expression statment")
    emitByte(OpCode.OP_POP) #you must need to pop the value after a expression is done
    
def forStatement():
    beginScope()
    consume(TokenType.LEFT_PAREN,"Expect ( after for")
    if match(TokenType.SEMICOLON):
        pass
    elif match(TokenType.VAR):
        varDeclaration()
    else:
        expressionStatement()
    consume(TokenType.SEMICOLON,"Expect ';'")
    #condition expression
    loopStart=currentChunk().count #current var declare point
    exitJump=-1
    if not match(TokenType.SEMICOLON):
        expression() #condition
        consume(TokenType.SEMICOLON,"Expect ';' after loop condition")
        exitJump=emitJump(OpCode.OP_JUMP_IF_FALSE)
        emitByte(OpCode.OP_POP)
    #increment
    if not match(TokenType.RIGHT_PAREN):
        bodyJump=emitJump(OpCode.OP_JUMP) #force jump
        incrementStart=currentChunk().count #jump back after execute the body
        expression()
        emitByte(OpCode.OP_POP)
        consume(TokenType.RIGHT_PAREN,"Expect ')' after for clauses")
        emitLoop(loopStart)
        loopStart=incrementStart
        patchJump(bodyJump)
    #the block
    statement()
    emitLoop(loopStart) #get back to the loopstart
    if exitJump!=-1:
        patchJump(exitJump)
        emitByte(OpCode.OP_POP)
    endScope()
    
def whileStatement():
    loopStart=currentChunk().count
    consume(TokenType.LEFT_PAREN,"Expect '(' after while")
    expression()
    consume(TokenType.RIGHT_PAREN,"Expect ')' after condition")
    exitJump=emitJump(OpCode.OP_JUMP_IF_FALSE)
    emitByte(OpCode.OP_POP)
    statement()
    emitLoop(loopStart)
    patchJump(exitJump)
    emitByte(OpCode.OP_POP)
    
    
def returnStatement():
    global current
    if current.type==FunctionType.TYPE_SCRIPT:
        error("Cant return from top level code")
    if match(TokenType.SEMICOLON):
        emitReturn()
    else:
        expression()
        consume(TokenType.SEMICOLON,"Expect ';' after return value")
        emitByte(OpCode.OP_RETURN)

def block():
    while not check(TokenType.RIGHT_BRACE) and not check(TokenType.EOF):
        declaration()
    consume(TokenType.RIGHT_BRACE,'expect } after block')

def beginScope():
    global current
    current.scopeDepth+=1
    
def endScope():
    global current
    current.scopeDepth-=1
    while current.localCount>0 and current.locals[current.localCount-1].depth>current.scopeDepth:
        emitByte(OpCode.OP_POP)
        current.localCount-=1
        
def ifStatement():
    consume(TokenType.LEFT_PAREN,"expect '(' after if")
    expression()
    consume(TokenType.RIGHT_PAREN,"expect ')' after if")
    thenJump=emitJump(OpCode.OP_JUMP_IF_FALSE) #return the offset to jump if condition is false we not have else here
    emitByte(OpCode.OP_POP) #notice that if false this is omiited and have not effect
    statement()
    elseJump=emitJump(OpCode.OP_JUMP)
    patchJump(thenJump)
    emitByte(OpCode.OP_POP) #if the condition is true these are also omitted
    if match(TokenType.ELSE):
        statement()
    patchJump(elseJump)
    
    

#detail parse rule
#the rule number and unary here are not going into higher precedence
#assume the token has been scan and another advance has been call
def number(canAssign:bool):
    global parser
    global globalSource
    start=parser.previous.start 
    length=parser.previous.length
    floatVal=float(globalSource[start:start+length])
    emitConstant(NUMBER_VAL(floatVal))

#prefix expression    
def grouping(canAssign:bool):
    expression()
    consume(TokenType.RIGHT_PAREN,"Expect ')' after expression")
    
    
def unary(canAssign:bool):
    global parser 
    operatorType=parser.previous.type
    #parse only with higher precedence
    parsePrecedence(Precedence.PREC_UNARY)
    if operatorType==TokenType.MINUS:
        emitByte(OpCode.OP_NEGATE)   
    if operatorType==TokenType.BANG:
        emitByte(OpCode.OP_NOT)
    else:
        pass
    
def binary(canAssign:bool):
    global parser
    operatorType=parser.previous.type
    rule=getRule(operatorType)
    prec=Precedence(int(rule.precedence)+1)
    parsePrecedence(prec)
    if operatorType==TokenType.PLUS:
        emitByte(OpCode.OP_ADD)
    elif operatorType==TokenType.MINUS:
        emitByte(OpCode.OP_SUBTRACT)
    elif operatorType==TokenType.STAR:
        emitByte(OpCode.OP_MULTIPLY)
    elif operatorType==TokenType.SLASH:
        emitByte(OpCode.OP_DIVIDE)
    elif operatorType==TokenType.BANG_EQUAL:
        emitBytes(OpCode.OP_EQUAL,OpCode.OP_NOT)
    elif operatorType==TokenType.EQUAL_EQUAL:
        emitByte(OpCode.OP_EQUAL)
    elif operatorType==TokenType.GREATER:
        emitByte(OpCode.OP_GREATER)
    elif operatorType==TokenType.GREATER_EQUAL:
        emitBytes(OpCode.OP_LESS,OpCode.OP_NOT)
    elif operatorType==TokenType.LESS:
        emitByte(OpCode.OP_LESS)
    elif operatorType==TokenType.LESS_EQUAL:
        emitBytes(OpCode.OP_GREATER,OpCode.OP_NOT)            
    return 

def literal(canAssign:bool):
    global parser 
    t=parser.previous.type
    if t==TokenType.FALSE:
        emitByte(OpCode.OP_FALSE)
    elif t==TokenType.NIL:
        emitByte(OpCode.OP_NIL)
    elif t==TokenType.TRUE:
        emitByte(OpCode.OP_TRUE)
    else:
        pass
    
def string(canAssign:bool):
    global parser 
    global globalSource
    #trim the quote
    start=parser.previous.start
    length=parser.previous.length
    source_str=globalSource[start+1:start+length-1]
    val=OBJ_VAL(copyString(source_str,len(source_str)))
    PLoxVM.vm.objects.appendleft(val)
    emitConstant(val)
    
def variable(canAssign:bool):
    global parser
    namedVariable(parser.previous,canAssign)
    
def and_(canAssign:bool):
    #in here we already parse the former part of the and expression
    #jump if false leave it's value on the stack as the result
    endJump=emitJump(OpCode.OP_JUMP_IF_FALSE)
    emitByte(OpCode.OP_POP)#if the value is true we pop,keep the next precedence result as it's result
    parsePrecedence(Precedence.PREC_AND)
    patchJump(endJump)
    
def or_(canAssign:bool):
    elseJump=emitJump(OpCode.OP_JUMP_IF_FALSE)
    endJump=emitJump(OpCode.OP_JUMP)
    patchJump(elseJump)
    emitByte(OpCode.OP_POP)
    parsePrecedence(Precedence.PREC_OR)
    patchJump(endJump)

#when call are called the function value it's already on the top of stack
def call_(canAssign:bool):
    argCount=argumentList()
    emitBytes(OpCode.OP_CALL,argCount)
    
def argumentList():
    argCount=0
    if not check(TokenType.RIGHT_PAREN):
        while True:
            expression()
            argCount+=1
            if argCount==255:
                error("Cant have more than 255 arguments")
            if not match(TokenType.COMMA):
                break
    consume(TokenType.RIGHT_PAREN,"Expect ')' after arguments.")
    return argCount
                
 
DEBUG_PRINT_CODE=True        
parser=Parser()
scanner=Scanner(None)
globalSource=str()
current=None
rules={
    int(TokenType.LEFT_PAREN):ParseRule(grouping,call_,Precedence.PREC_CALL),
    int(TokenType.RIGHT_PAREN):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.LEFT_BRACE):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.RIGHT_BRACE):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.COMMA):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.DOT):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.MINUS):ParseRule(unary,binary,Precedence.PREC_TERM),
    int(TokenType.PLUS):ParseRule(None,binary,Precedence.PREC_TERM),
    int(TokenType.SEMICOLON):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.SLASH):ParseRule(None,binary,Precedence.PREC_FACTOR),
    int(TokenType.STAR):ParseRule(None,binary,Precedence.PREC_FACTOR),
    int(TokenType.BANG):ParseRule(unary,None,Precedence.PREC_NONE),
    int(TokenType.BANG_EQUAL):ParseRule(None,binary,Precedence.PREC_EQUALITY),
    int(TokenType.EQUAL):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.EQUAL_EQUAL):ParseRule(None,binary,Precedence.PREC_EQUALITY),
    int(TokenType.GREATER):ParseRule(None,binary,Precedence.PREC_COMPARISON),
    int(TokenType.GREATER_EQUAL):ParseRule(None,binary,Precedence.PREC_COMPARISON),
    int(TokenType.LESS):ParseRule(None,binary,Precedence.PREC_COMPARISON),
    int(TokenType.LESS_EQUAL):ParseRule(None,binary,Precedence.PREC_COMPARISON),
    int(TokenType.IDENTIFER):ParseRule(variable,None,Precedence.PREC_NONE),
    int(TokenType.STRING):ParseRule(string,None,Precedence.PREC_NONE),
    int(TokenType.NUMBER):ParseRule(number,None,Precedence.PREC_NONE),
    int(TokenType.AND):ParseRule(None,and_,Precedence.PREC_AND),
    int(TokenType.CLASS):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.ELSE):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.FALSE):ParseRule(literal,None,Precedence.PREC_NONE),
    int(TokenType.FOR):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.FUN):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.IF):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.NIL):ParseRule(literal,None,Precedence.PREC_NONE),
    int(TokenType.OR):ParseRule(None,or_,Precedence.PREC_OR),
    int(TokenType.PRINT):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.RETURN):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.SUPER):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.THIS):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.TRUE):ParseRule(literal,None,Precedence.PREC_NONE),
    int(TokenType.VAR):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.WHILE):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.TOKEN_ERROR):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.EOF):ParseRule(None,None,Precedence.PREC_NONE)   
}

        
def parsePrecedence(precedence:Precedence):
    global parser
    advance()
    #get the rule of previous token,say token number get a number prefix parse fun
    prefixRule=getRule(parser.previous.type).prefix
    if prefixRule is None:
        error("Expect expression")
        return 
    canAssign=precedence<=Precedence.PREC_ASSIGNMENT
    #prefix expression is consume,and it dont advance
    #print(prefixRule.__name__)
    prefixRule(canAssign) 
    #note:here we still on the processed token, the token we want to handle still in current
    #example, 2+5, we still current in +,and + has higher precedence than 2
    #then we stop at current pointer at 5
    #example: 2+5+7,the parser reach binary and then binary call precedence itself, precedence function are called resuviely to move on 
    #this means this rule should finish more important rule first on parser
    #like *5+2
    while precedence<=getRule(parser.current.type).precedence:
        advance()
        infixRule=getRule(parser.previous.type).infix
        #print(infixRule.__name__)
        infixRule(canAssign)
    if canAssign and match(TokenType.EQUAL):
        error("Invalid assignment target")
        


def getRule(type:TokenType)->ParseRule:
    global rules
    return rules.get(int(type))

#remove chunk
def compile(source)->ObjFunction:
    global scanner
    global parser
    global globalSource
    global current
    globalSource=source
    scanner=Scanner(source)
    compiler=Compiler()
    parser=Parser()
    #impilicit top level function like main, and it store it's own initial chunk
    initCompiler(compiler,FunctionType.TYPE_SCRIPT)
    advance() #consume one token to parser
    #expression()
    #consume final eof token
    #
    while match(TokenType.EOF) is False:
        declaration()
    #function=endCompiler()
    return None if parser.hadError else endCompiler()
     
def advance():
    global scanner
    global parser
    parser.previous=parser.current
    while True:
        parser.current=scanner.scanToken()
        if parser.current.type!=TokenType.TOKEN_ERROR:
            break 
        #error token has special start field
        errorAtCurrent(parser.current.start)
        
def errorAtCurrent(message:str):
    global parser
    errorAt(parser.current,message)
    
def error(message:str):
    global parser
    errorAt(parser.previous,message)
    
def errorAt(token:Token,message:str):
    global parser
    if parser.panicMode:
        return
    parser.panicMode=True
    wrong_info="[line {}] Error".format(token.line)
    if token.type==TokenType.EOF:
        wrong_info+=" at end"
    elif token.type==TokenType.TOKEN_ERROR:
        pass
    else:
        wrong_info+=" at start {} with length {}".format(token.length,token.start)
    wrong_info+=": {}".format(message)
    print(wrong_info)
    parser.hadError=True
  


def consume(type,message):
    global parser
    global scanner
    if parser.current.type==type:
        advance()
        return 
    errorAtCurrent(message)
    
def match(type:TokenType):
    if not check(type):
        return False
    else:
        advance()
    return True 

def check(type:TokenType):
    global parser 
    return parser.current.type==type

def synchronize():
    global parser
    parser.panicMode=False
    while parser.current.type!=TokenType.EOF:
        if parser.previous.type==TokenType.SEMICOLON:
            return
        start_point=[TokenType.CLASS,TokenType.FUN,TokenType.VAR,TokenType.FOR, \
               TokenType.IF,TokenType.WHILE,TokenType.PRINT,TokenType.RETURN]
        if parser.current.type in start_point:
            return 
        advance()
          
def emitByte(byte):
    global parser
    writeChunk(currentChunk(),byte,parser.previous.line)
    
def currentChunk():
    global current 
    return current.function.chunk

def endCompiler():
    global parser
    global current 
    emitReturn()
    function=current.function
    if DEBUG_PRINT_CODE is True:
        if not parser.hadError:
            info=function.name.chars if function.name is not None else "<script>"
            #disassembleChunk(currentChunk(),"")
    current=current.enclosing
    return function
    
def emitReturn():
    emitByte(OpCode.OP_NIL)
    emitByte(OpCode.OP_RETURN)
    
def emitBytes(byte1,byte2):
    emitByte(byte1)
    emitByte(byte2)
    
def emitConstant(value:Value):
    emitBytes(OpCode.OP_CONSTANT,makeConstant(value))
    
def emitJump(instruction):
    emitByte(instruction)
    emitByte(0xff)
    emitByte(0xff) #16 bits of offset code to jump
    return currentChunk().count-2

def emitLoop(loopStart:int):
    emitByte(OpCode.OP_LOOP)
    offset=currentChunk().count-loopStart+2
    if offset>65536:
        error("Too much for loop body")
    emitByte((offset>>8) & 0xff)
    emitByte(offset & 0xff)

#this is the the idx of jump command
def patchJump(offset):
    jump=currentChunk().count-offset-2
    #return to 
    if jump>65536:
        error("Too much to jump over")
    currentChunk().code[offset]= ((jump>>8) & 0xff)
    currentChunk().code[offset+1]= (jump & 0xff)
    
    
def makeConstant(value:Value):
    constant_idx=addConstant(currentChunk(),value)
    if constant_idx>256:
        error("Too many constant in one chunk")
        return 0
    return constant_idx

def initCompiler(compiler:Compiler,type:FunctionType):
    global current
    global globalSource
    global parser 
    local=Local()
    local.depth=0
    local.name.start=""
    local.name.length=0
    compiler.locals[0]=local #first slot for internal vm use
    compiler.localCount=1
    compiler.scopeDepth=0
    compiler.type=type
    compiler.function=newFunction()
    if type==FunctionType.TYPE_SCRIPT:
        mainName="main"
        compiler.function.name=copyString(mainName,4)
    compiler.enclosing=current
    current=compiler
    if type!=FunctionType.TYPE_SCRIPT:
        start=parser.previous.start
        length=parser.previous.length
        nameStr=globalSource[start:start+length]
        print("init compiler for {}".format(nameStr))
        current.function.name=copyString(nameStr,length)
    


    
    
    
    
    
    
    
    