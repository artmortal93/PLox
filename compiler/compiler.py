from scanner import *
from debug import *
from chunk import *
from chunk import OpCode
from value import *

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
    

#detail parse rule
#the rule number and unary here are not going into higher precedence
#assume the token has been scan and another advance has been call
def number():
    global parser
    global globalSource
    start=parser.previous.start 
    length=parser.previous.length
    floatVal=float(globalSource[start:start+length])
    emitConstant(NUMBER_VAL(floatVal))

#prefix expression    
def grouping():
    expression()
    consume(TokenType.RIGHT_PAREN,"Expect ')' after expression")
    
    
def unary():
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
    
def binary():
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
    return 

def literal():
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
    

    
 
DEBUG_PRINT_CODE=True        
compilingChunk=chunk.Chunk(None)
parser=Parser()
scanner=Scanner(None)
globalSource=str()
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
    int(TokenType.BANG_EQUAL):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.EQUAL):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.EQUAL_EQUAL):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.GREATER):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.GREATER_EQUAL):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.LESS):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.LESS_EQUAL):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.IDENTIFER):ParseRule(None,None,Precedence.PREC_NONE),
    int(TokenType.STRING):ParseRule(None,None,Precedence.PREC_NONE),
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
    #prefix expression is consume,and it dont advance
    print(prefixRule.__name__)
    prefixRule() 
    #note:here we still on the processed token, the token we want to handle still in current
    #example, 2+5, we still current in +,and + has higher precedence than 2
    #then we stop at current pointer at 5
    #example: 2+5+7,the parser reach binary and then binary call precedence itself, precedence function are called resuviely to move on 
    #this means this rule should finish more important rule first on parser
    #like *5+2
    while precedence<=getRule(parser.current.type).precedence:
        advance()
        infixRule=getRule(parser.previous.type).infix
        infixRule()
        


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
    compilingChunk=chunk
    parser=Parser()
    advance() #consume one token to parser
    expression()
    #consume final eof token
    consume(TokenType.EOF,"Expect end of espression")
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
    
def emitByte(byte):
    global parser
    chunk.writeChunk(currentChunk(),byte,parser.previous.line)
    
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


    
    
    
    
    
    
    
    