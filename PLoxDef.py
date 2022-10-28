
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

    def toString(self)->str:
        return str(self.type)+" "+self.lexeme+" "+str(self.literal)



class Expr(ABC):
    pass

class Binary(Expr): 
    def __init__(self,left:Expr,operator:Token,right:Expr):
        self.left=left
        self.operator=operator
        self.right=right

class Grouping(Expr): 
    def __init__(self,expression:Expr):
        self.expression=expression

class Literal(Expr): 
    def __init__(self,value:object):
        self.value=value

class Unary(Expr): 
    def __init__(self,operator:Token,right:Expr):
        self.operator=operator
        self.right=right



