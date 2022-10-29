from PLoxDef import *
import PLox

#generate Tree of expression(AST)
class Parser:
    def __init__(self, tokens, *args, **kwargs):
        self.tokens=tokens
        self.current=0 #the one are waiting to check token but not check yet

    def isAtEnd(self)->bool:
        return self.peek().type is TokenType.EOF

    def peek(self)->Token:
        return self.tokens[self.current]

    def previous(self)->Token:
        return self.tokens[self.current-1]

    def advance(self)->Token:
        if not self.isAtEnd():
            self.current+=1
        return self.previous()

    def check(self,type:TokenType)->bool:
        if self.isAtEnd():
            return False
        return self.peek().type==type

    #match any type in types, then advance
    def match(self, *types)->bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True #? then why *args
        return False

    def consume(self,type:TokenType, message:str):
        if self.check(type):
            return self.advance()
        next=self.peek()
        raise self.error(next,message)

    def error(self,token,message):
        PLox.PLox.tokenError(token,message)
        return ParseError()

    #decsent parser starts
    def expression(self)->Expr:
        return self.equality()

    def equality(self)->Expr:
        #note that * are tranlated into while loop
        expr=self.comparison()
        while self.match(TokenType.BANG_EQUAL,TokenType.EQUAL):
            operator=self.previous()
            right=self.comparison()
            expr=Binary(expr,operator,right)
        return expr

    def comparison(self)->Expr:
        expr=self.term()
        while self.match(TokenType.GREATER,TokenType.GREATER_EQUAL,TokenType.LESS,TokenType.LESS_EQUAL):
            operator=self.previous()
            right=self.term()
            expr=Binary(expr,operator,right)
        return expr

    def term(self)->Expr:
        expr=self.factor()
        while self.match(TokenType.MINUS,TokenType.PLUS):
            operator=self.previous()
            right=self.factor()
            expr=Binary(expr,operator,right)
        return expr

    def factor(self)->Expr:
        expr=self.unary()
        while self.match(TokenType.SLASH,TokenType.STAR):
            operator=self.previous()
            right=self.unary()
            expr=Binary(expr,operator,right)
        return expr 

    def unary(self)->Expr:
        if self.match(TokenType.BANG,TokenType.MINUS):
            operator=self.previous()
            right=self.unary()
            return Unary(operator,right)
        else:
            return self.primary()

    def primary(self)->Expr:
        if self.match(TokenType.FALSE):
            return Literal(False)
        elif self.match(TokenType.TRUE):
            return Literal(True)
        elif self.match(TokenType.NIL):
            return Literal(None)
        elif self.match(TokenType.NUMBER,TokenType.STRING):
            return Literal(self.previous().literal)
        elif self.match(TokenType.LEFT_PAREN):
            expr=self.expression() #in this case. a expression has been consume and advanced
            self.consume(TokenType.RIGHT_PAREN,'Expect ) after expression.')
            return Grouping(expr)
        #the error of other not processed yet token (or/if/while/for)
        raise self.error(self.peek(),"Expect expression.")

    #reset to another possible statment if error was met, but the error should not be
    #critical
    def synchornize(self):
        self.advance() #omit the wrong token
        while not self.isAtEnd():
            if self.previous().type==TokenType.SEMICOLON:
                return
            typeToStart=[TokenType.CLASS,TokenType.FUN,TokenType.VAR,TokenType.FOR,TokenType.IF,TokenType.WHILE,TokenType.PRINT,TokenType.RETURN]
            if self.peek().type in typeToStart:
                #self.advance()
                return
            self.advance()

    def parse(self):
        try:
            return self.expression()
        except ParseError:
            return None





