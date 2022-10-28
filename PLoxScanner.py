from PLoxDef import TokenType,Token
import PLox #solve circular import


keywords={
    'and':TokenType.AND,
    'class':TokenType.CLASS,
    'else':TokenType.ELSE,
    'false':TokenType.FALSE,
    'for':TokenType.FOR,
    'fun':TokenType.FUN,
    'if':TokenType.IF,
    'nil':TokenType.NIL,
    'or':TokenType.OR,
    'print':TokenType.PRINT,
    'return':TokenType.PRINT,
    'super':TokenType.SUPER,
    'this':TokenType.THIS,
    'true':TokenType.TRUE,
    'var':TokenType.VAR,
    'while':TokenType.WHILE
}

class Scanner(object):
    def __init__(self, source:str):
        super().__init__()
        self.source=source
        self.tokens=list()
        self.start=0 #point to the first char of current lexeme
        self.current=0#point to the current char of being considered in lexeme
        self.line=1

    def scanToken(self):
        c=self.advance()
        if c=='(':
            self.addToken(TokenType.LEFT_PAREN)
        elif c==')':
            self.addToken(TokenType.RIGHT_PAREN)
        elif c=='{':
            self.addToken(TokenType.LEFT_BRACE)
        elif c=='}':
            self.addToken(TokenType.RIGHT_BRACE)
        elif c==',':
            self.addToken(TokenType.COMMA)
        elif c=='.':
            self.addToken(TokenType.DOT)
        elif c=='-':
            self.addToken(TokenType.MINUS)
        elif c=='+':
            self.addToken(TokenType.PLUS)
        elif c==';':
            self.addToken(TokenType.SEMICOLON)
        elif c=='*':
            self.addToken(TokenType.STAR)
        #case of one char above
        elif c=="!":
            if self.match('='):
                self.addToken(TokenType.BANG_EQUAL)
            else:
                self.addToken(TokenType.BANG)
        elif c=='=':
            if self.match('='):
                self.addToken(TokenType.LESS_EQUAL)
            else:
                self.addToken(TokenType.EQUAL)
        elif c=='<':
            if self.match('='):
                self.addToken(TokenType.LESS_EQUAL)
            else:
                self.addToken(TokenType.LESS)
        elif c=='>':
            if self.match('='):
                self.addToken(TokenType.GREATER_EQUAL)
            else:
                self.addToken(TokenType.GREATER)
        elif c=='/':
            if self.match('/'): #case:comment, skip all line
                while self.peek()!='\n' and not self.isAtEnd():
                    self.advance()
            else:
                self.addToken(TokenType.SLASH)
        elif c in [' ','\r','\t']:
            pass
        elif c=='\n':
            self.line+=1
            pass
        #case for two consequent char
        #handling the string literals
        elif c=='"':
            self.string() #using this way to handle <> in xml
        #for wrong lexical character error handling
        else:
            if self.isDigit(c):
                self.number()
            elif self.isAlpha(c):
                self.identifier()
            else:
                PLox.PLox.error(self.line,"Unexpecterd Character.")
                
   #utility functions
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

    #advance but do not consumer the character
    def peek(self)->str:
        if self.isAtEnd():
            return '\0'
        else:
            return self.source[self.current]


    def peekNext(self)->str:
        if self.current+1>=len(self.source):
            return '\0'
        return self.source[self.current+1]

    def string(self):
        while self.peek()!='"' and not self.isAtEnd():
            if self.peek()=='\n':
                self.line+=1
            self.advance()
        #case:reach the end of file
        if self.isAtEnd():
             PLox.error(self.line,"Unterminated string.")
             return
        self.advance()
        value=self.source[self.start+1:self.current-1] #trim the ""
        self.addToken(TokenType.STRING,value)

    def isDigit(self,c:str)->bool:
        return c>='0' and c<='9'

    def isAlpha(self,c:str)->bool:
        return (c>='a' and c<='z') or (c>='A' and c<='Z') or c=='_'

    def isAlphaNumeric(self,c:str)->bool:
        return self.isAlpha(c) or self.isDigit(c)

    def number(self):
        while self.isDigit(self.peek()):
            self.advance()
        if self.peek()=='.' and self.isDigit(self.peekNext()):
            self.advance()
            while self.isDigit(self.peek()):
                self.advance()
        self.addToken(TokenType.NUMBER,float(self.source[self.start:self.current]))
    #utility functions end

    def identifier(self):
        while self.isAlphaNumeric(self.peek()):
            self.advance()
        text=self.source[self.start:self.current]
        type=keywords.get(text)
        if type is None:
            type=TokenType.IDENTIFER
        self.addToken(type)

    def scanTokens(self)->list:
        while not self.isAtEnd():
            self.start = self.current
            self.scanToken()
        self.tokens.append(Token(TokenType.EOF,"",None,self.line))
        return self.tokens

    
    def addToken(self,type:TokenType,literal=None):
        text=self.source[self.start:self.current]
        self.tokens.append(Token(type,text,literal,self.line))

