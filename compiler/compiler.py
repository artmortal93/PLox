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
    
class Local:
    def __init__(self) -> None:
        self.name=Token()
        self.depth=0
        
class Compiler:
    def __init__(self) -> None:
        self.locals=[None]*256
        self.localCount=0
        self.scopeDepth=0
        
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
    else:
        statement()
    if parser.panicMode:
        synchronize()
        
def varDeclaration():
    #if we are in block that scope>0 parse and define do nothing
    global_idx=parseVariable("Expect variable name")
    if match(TokenType.EQUAL):
        expression()#only keep variable in stack
    else:
        emitByte(OpCode.OP_NIL)
    consume(TokenType.SEMICOLON,"expect ';' after value.")
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
    elif match(TokenType.TOKEN_IF):
        ifStatement()
    elif match(TokenType.LEFT_BRACE):
        beginScope()
        block()
        endScope()
    else:
        expressionStatement()
        
def printStatement():
    expression()
    consume(TokenType.SEMICOLON,"expect ';' after value.")
    emitByte(OpCode.OP_PRINT)
    
def expressionStatement():
    expression()
    consume(TokenType.SEMICOLON,"expect ';' after value.")
    emitByte(OpCode.OP_POP) #you must need to pop the value after a expression is done
    
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
        emitByte(OpCode.POP)
        current.localCount-=1
        
def ifStatement():
    consume(TokenType.LEFT_PAREN,"expect '(' after if")
    expression()
    consume(TokenType.RIGHT_PAREN,"expect ')' after if")
    thenJump=emitJump(OpCode.OP_JUMP_IF_FALSE) #return the offset to jump if condition is false we not have else here
    statement()
    elseJump=emitJump(OpCode.OP_JUMP)
    patchJump(thenJump)
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
    

    
 
DEBUG_PRINT_CODE=True        
compilingChunk=Chunk(None)
parser=Parser()
scanner=Scanner(None)
globalSource=str()
current=None
rules={
    int(TokenType.LEFT_PAREN):ParseRule(grouping,None,Precedence.PREC_NONE),
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
    int(TokenType.AND):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.CLASS):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.ELSE):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.FALSE):ParseRule(literal,None,Precedence.PREC_NONE),
    int(TokenType.FOR):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.FUN):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.IF):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.NIL):ParseRule(literal,None,Precedence.PREC_NONE),
    int(TokenType.OR):ParseRule(None,None,Precedence.PREC_NONE),
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
        infixRule(canAssign)
    if canAssign and match(TokenType.EQUAL):
        error("Invalid assignment target")
        


def getRule(type:TokenType)->ParseRule:
    global rules
    return rules.get(int(type))


def compile(source,chunk)->bool:
    global scanner
    global parser
    global compilingChunk
    global globalSource
    globalSource=source
    scanner=Scanner(source)
    compiler=Compiler()
    initCompiler(compiler)
    compilingChunk=chunk
    parser=Parser()
    advance() #consume one token to parser
    #expression()
    #consume final eof token
    #
    while match(TokenType.EOF) is False:
        declaration()
    endCompiler()
    return not parser.hadError
     
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
    errorAt(parser,parser.current,message)
    
def error(message:str):
    global parser
    errorAt(parser,parser.previous,message)
    
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
    global compilingChunk
    return compilingChunk

def endCompiler():
    global parser 
    emitReturn()
    if DEBUG_PRINT_CODE is True:
        if not parser.hadError:
            disassembleChunk(currentChunk(),"code")
    
def emitReturn():
    emitByte(OpCode.OP_RETURN)
    
def emitBytes(byte1,byte2):
    emitByte(byte1)
    emitByte(byte2)
    
def emitConstant(value:Value):
    emitBytes(OpCode.OP_CONSTANT,makeConstant(value))
    
def makeConstant(value:Value):
    constant_idx=addConstant(currentChunk(),value)
    if constant_idx>256:
        error("Too many constatn in one chunk")
        return 0
    return constant_idx

def initCompiler(compiler:Compiler):
    global current 
    compiler.localCount=0
    compiler.scopeDepth=0
    current=compiler
    


    
    
    
    
    
    
    
    