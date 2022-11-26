from enum import Enum,IntEnum

class TokenType(IntEnum):
    LEFT_PAREN=1
    RIGHT_PAREN=2
    LEFT_BRACE=3
    RIGHT_BRACE=4
    COMMA=5
    DOT=6
    MINUS=7
    PLUS=8
    SEMICOLON=9
    SLASH=10
    STAR=11
    #one or two char tokens
    BANG=12
    BANG_EQUAL=13
    EQUAL=14
    EQUAL_EQUAL=15
    GREATER=16
    GREATER_EQUAL=17
    LESS=18
    LESS_EQUAL=19
    #literals
    IDENTIFER=20
    STRING=21
    NUMBER=22
    #KEYWORDS
    AND=23
    CLASS=24
    ELSE=25
    FALSE=26
    FUN=27
    FOR=28
    IF=29
    NIL=30
    OR=31
    PRINT=32
    RETURN=33
    SUPER=34
    THIS=35
    TRUE=36
    VAR=37
    WHILE=38
    EOF=39
    TOKEN_ERROR=40



class Token(object):
    def __init__(self,type:TokenType=TokenType.TOKEN_ERROR,start=0,length:int=0,line:int=0):
        self.type=type
        self.start=start #start pointer in the source to indicate the lexeme
        self.length=length
        self.line=line


class Scanner(object):
    def __init__(self, source:str):
        super().__init__()
        self.source=source
        self.tokens=list()
        self.start=0 #point to the first char of current lexeme
        self.current=0#point to the current char of being considered in lexeme
        self.line=1
        
        
    def match(self,expected:str)->bool:
        if self.isAtEnd():
            return False
        if self.source[self.current]!=expected:
            return False
        self.current+=1
        return True
    
    def isAtEnd(self)->bool:
        return self.current>=len(self.source)

    def advance(self)->str:
        self.current+=1
        return self.source[self.current-1]
    
    def isDigit(self,c:str)->bool:
        return c>='0' and c<='9'

    def isAlpha(self,c:str)->bool:
        return (c>='a' and c<='z') or (c>='A' and c<='Z') or c=='_'

    def isAlphaNumeric(self,c:str)->bool:
        return self.isAlpha(c) or self.isDigit(c)

    #advance but do not consumer the character
    def peek(self)->str:
        if self.isAtEnd():
            return '\0'
        else:
            return self.source[self.current]
        
    def skipWhiteSpace(self):
        while True:
            c=self.peek()
            if c in [' ','\r','\t']:
                self.advance()
            elif c=='\n':
                self.line+=1
                self.advance()
            elif c=='/':
                if self.peekNext()=='/':
                    while self.peek()!='\n' and not self.isAtEnd():
                        self.advance() 
                else:
                    return 
            else:
                break
            

    def peekNext(self)->str:
        if self.current+1>=len(self.source):
            return '\0'
        return self.source[self.current+1]
    
    def scanToken(self):
        self.skipWhiteSpace()
        self.start=self.current
        if self.isAtEnd():
            return self.makeToken(TokenType.EOF)
        c=self.advance()
        if self.isAlpha(c):
            return self.identifier()
        if self.isDigit(c):
            return self.number()
        if c=='(':
            return self.makeToken(TokenType.LEFT_PAREN)
        elif c==')':
            return self.makeToken(TokenType.RIGHT_PAREN)
        elif c=='{':
            return self.makeToken(TokenType.LEFT_BRACE)
        elif c=='}':
            return self.makeToken(TokenType.RIGHT_BRACE)
        elif c==',':
            return self.makeToken(TokenType.COMMA)
        elif c=='.':
            return self.makeToken(TokenType.DOT)
        elif c=='-':
            return self.makeToken(TokenType.MINUS)
        elif c=='+':
            return self.makeToken(TokenType.PLUS)
        elif c==';':
            return self.makeToken(TokenType.SEMICOLON)
        elif c=='*':
            return self.makeToken(TokenType.STAR)
        elif c=='/':
            return self.makeToken(TokenType.SLASH)
        elif c=='!':
            t=TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG
            return self.makeToken(t)
        elif c=='=':
            t=TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL
            return self.makeToken(t)
        elif c=='<':
            t=TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS
            return self.makeToken(t)
        elif c=='>':
            t=TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER
            return self.makeToken(t)
        elif c=='"':
            return self.string()
        
        return self.errorToken("Unexpected character.")
            
    def makeToken(self,type:TokenType)->Token:
        token=Token()
        token.type=type
        token.start=self.start
        token.length=self.current-self.start
        token.line=self.line
        return token 
    
        
    def errorToken(self,message)->Token:
        token=Token()
        token.type=TokenType.TOKEN_ERROR
        token.start=message
        token.length=len(message)
        token.line=self.line
        return token
    
    def string(self):
        while self.peek()!='"' and not self.isAtEnd():
            if self.peek()=='\n':
                self.line+=1
            self.advance()
        if self.isAtEnd():
            return self.errorToken("Unterminated String")
        self.advance()
        return self.makeToken(TokenType.STRING)
    
    def number(self):
        while self.isDigit(self.peek()):
            self.advance()
        if self.peek()=='.' and self.isDigit(self.peekNext()):
            self.advance()
            while self.isDigit(self.peek()):
                self.advance()
        return self.makeToken(TokenType.NUMBER)
    
    def identifier(self):
        while self.isAlpha(self.peek()) or self.isDigit(self.peek()):
            self.advance()
        return self.makeToken(self.identifierType())
    
    def identifierType(self):
        c=self.source[self.start]
        if c=='a':
            return self.checkKeyword(1,2,"nd",TokenType.AND)
        elif c=='c':
            return self.checkKeyword(1,4,"lass",TokenType.CLASS)
        elif c=='e':
            return self.checkKeyword(1,3,"lse",TokenType.ELSE)
        elif c=='f':
            if self.current-self.start>1:
                c1=self.source[self.start+1]
                if c1=='a':
                    return self.checkKeyword(2,3,"lse",TokenType.FALSE)
                elif c1=='o':
                    return self.checkKeyword(2,1,"r",TokenType.FOR)
                elif c1=='u':
                    return self.checkKeyword(2,1,'n',TokenType.FUN)
        elif c=='i':
            return self.checkKeyword(1,1,"f",TokenType.IF)
        elif c=='n':
            return self.checkKeyword(1,2,'il',TokenType.NIL)
        elif c=='o':
            return self.checkKeyword(1,1,'r',TokenType.OR)
        elif c=='p':
            return self.checkKeyword(1,4,'rint',TokenType.PRINT)
        elif c=='r':
            return self.checkKeyword(1,5,'eturn',TokenType.RETURN)
        elif c=='s':
            return self.checkKeyword(1,4,"uper",TokenType.SUPER)
        elif c=='t':
            if self.current-self.start>1:
                c1=self.source[self.start+1]
                if c1=='h':
                    return self.checkKeyword(2,2,"is",TokenType.THIS)
                elif c1=="r":
                    return self.checkKeyword(2,2,"ue",TokenType.TRUE)
                else:
                    pass
        elif c=='v':
            return self.checkKeyword(1,2,"ar",TokenType.VAR)
        elif c=='w':
            return self.checkKeyword(1,4,"hile",TokenType.WHILE)
        return TokenType.IDENTIFER
        
    def checkKeyword(self,start,length,rest,Type):
        if self.current-self.start==start+length and rest==self.source[self.start+start:self.start+start+length]:
            return Type
        return TokenType.IDENTIFER
        
       
        
    
        
    
    
    
    