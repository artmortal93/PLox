
from enum import Enum
from abc import ABC, abstractmethod

class TokenType(Enum):
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

#store token information
class Token(object):
    def __init__(self,type:TokenType,lexeme:str,literal,line:int):
        self.type=type
        self.lexeme=lexeme
        self.literal=literal
        self.line=line

    def __str__(self)->str:
        return str(self.type)+" "+self.lexeme+" "+str(self.literal)

class ParseError(Exception):
    """Base class for other exceptions"""
    pass

class Expr(ABC):
    @abstractmethod
    def accept(self,visitor):
        pass

class Binary(Expr): 
    def __init__(self,left:Expr,operator:Token,right:Expr):
        self.left=left
        self.operator=operator
        self.right=right

    def accept(self,visitor):
        return visitor.visitBinaryExpr(self)


class Grouping(Expr): 
    def __init__(self,expression:Expr):
        self.expression=expression

    def accept(self,visitor):
        return visitor.visitGroupingExpr(self)

class Literal(Expr): 
    def __init__(self,value:object):
        self.value=value

    def accept(self,visitor):
        return visitor.visitLiteralExpr(self)

class Unary(Expr): 
    def __init__(self,operator:Token,right:Expr):
        self.operator=operator
        self.right=right

    def accept(self,visitor):
        return visitor.visitUnaryExpr(self)

class Visitor(ABC):
    @abstractmethod
    def visitBinaryExpr(self,Expr):
        pass

    @abstractmethod
    def visitGroupingExpr(self,Expr):
        pass

    @abstractmethod
    def visitLiteralExpr(self,Expr):
        pass

    @abstractmethod
    def visitUnaryExpr(self,Expr):
        pass

class ASTPrinter(Visitor):
    #=interprete method
    def print(self,expr:Expr):
        return expr.accept(self)

    def visitBinaryExpr(self, expr:Binary):
        return self.parenthesize(expr.operator.lexeme,expr.left,expr.right)
        

    def visitGroupingExpr(self, expr:Grouping):
        return self.parenthesize('group',expr.expression)

    def visitLiteralExpr(self, expr:Literal):
        if (expr.value==None):
            return "nil"
        return str(expr.value)

    def visitUnaryExpr(self, expr:Unary):
        return self.parenthesize(expr.operator.lexeme,expr.right)
    
    def parenthesize(self,name:str,*exprs):
        output='('+name
        for expr in exprs:
            output+=' '
            output+=expr.accept(self) #recurive here
        output+=')'
        return output






