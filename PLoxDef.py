
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

class FunctionType(Enum):
    NONE=0
    FUNCTION=1
    INITIALIZER=2
    METHOD=3

class ClassType(Enum):
    NONE=0
    CLASS=1
    SUBCLASS=2

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

class RunTimeError(Exception):
    def __init__(self,token,message):
        super().__init__()
        self.token=token
        self.message=message

class ReturnException(Exception):
    def __init__(self,value):
        super().__init__(value)
        self.value=value


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

#Variable is not easy to recognized as literal
class Variable(Expr):
    def __init__(self,name:Token):
        self.name=name

    def accept(self,visitor):
        return visitor.visitVariableExpr(self)

class Assign(Expr):
    def __init__(self,name:Token,value:Expr):
        self.name=name
        self.value=value

    def accept(self,visitor):
        return visitor.visitAssignExpr(self)

class Logical(Expr):
    def __init__(self,left:Expr,operator:Token,right:Expr):
        self.left=left
        self.operator=operator
        self.right=right

    def accept(self,visitor):
        return visitor.visitLogicalExpr(self)

class Call(Expr):
    def __init__(self,callee:Expr,paren:Token,arguments:list):
        self.callee=callee
        self.paren=paren #for record runtime error on function only
        self.arguments=arguments


    def accept(self,visitor):
        return visitor.visitCallExpr(self)

#the dot accessor of class for method and member
class Get(Expr):
    def __init__(self,obj:Expr,name:Token):
        self.obj=obj
        self.name=name

    def accept(self,visitor):
        return visitor.visitGetExpr(self)

class Set(Expr):
    def __init__(self,obj:Expr,name:Token,value:Expr):
        self.obj=obj
        self.name=name
        self.value=value

    def accept(self,visitor):
        return visitor.visitSetExpr(self)

class This(Expr):
    def __init__(self,keyword:Token):
        self.keyword=keyword

    def accept(self,visitor):
        return visitor.visitThisExpr(self)

class Super(Expr):
    def __init__(self,keyword:Token,method:Token):
        self.keyword=keyword
        self.method=method

    def accept(self,visitor):
        return visitor.visitSuperExpr(self)




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

    @abstractmethod
    def visitVariableExpr(self,Expr):
        pass

    @abstractmethod
    def visitAssignExpr(self,Expr):
        pass

    @abstractmethod
    def visitLogicalExpr(self,Expr):
        pass

    @abstractmethod
    def visitCallExpr(self,Expr):
        pass

    @abstractmethod
    def visitGetExpr(self,Expr):
        pass

    @abstractmethod
    def visitSetExpr(self,Expr):
        pass

    @abstractmethod
    def visitThisExpr(self,Expr):
        pass

    @abstractmethod
    def visitSuperExpr(self,Expr):
        pass

class StmtVisitor(ABC):
    @abstractmethod
    def visitExpressionStmt(self,expression):
        pass

    @abstractmethod
    def visitPrintStmt(self,expression):
        pass

    @abstractmethod
    def visitVarStmt(self,expression):
        pass

    @abstractmethod
    def visitBlockStmt(self,expression):
        pass

    @abstractmethod
    def visitIfStmt(self,expression):
        pass
    
    @abstractmethod
    def visitWhileStmt(self,expression):
        pass

    @abstractmethod
    def visitFunctionStmt(self,expression):
        pass

    @abstractmethod
    def visitReturnStmt(self,expression):
        pass

    @abstractmethod
    def visitClassStmt(self,expression):
        pass

class Stmt(ABC):
    @abstractmethod
    def accept(self,visitor):
        pass

class Expression(Stmt):#it means expression statment,nnot Expr
    def __init__(self,expression:Expr):
        self.expression=expression

    def accept(self,visitor:StmtVisitor):
        return visitor.visitExpressionStmt(self)

class Print(Stmt):
    def __init__(self,expression:Expr):
        self.expression=expression

    def accept(self,visitor:StmtVisitor):
        return visitor.visitPrintStmt(self)

class Var(Stmt):
    def __init__(self,name:Token,initializer:Expr):
        self.initializer=initializer
        self.name=name

    def accept(self, visitor):
        return visitor.visitVarStmt(self)

class Block(Stmt):
    def __init__(self,statments:list):
        self.statments=statments
     
    def accept(self, visitor):
        return visitor.visitBlockStmt(self)

class If(Stmt):
    def __init__(self,condition:Expr,thenBranch:Stmt,elseBranch:Stmt):
        self.condition=condition;
        self.thenBranch=thenBranch
        self.elseBranch=elseBranch

    def accept(self,visitor):
        return visitor.visitIfStmt(self)

class While(Stmt):
    def __init__(self,condition:Expr,body:Stmt):
        self.condition=condition;
        self.body=body

    def accept(self,visitor):
        return visitor.visitWhileStmt(self)

class Function(Stmt):
    def __init__(self,name:Token,params:list,body:list):
        self.name=name
        self.params=params
        self.body=body

    def accept(self,visitor):
        return visitor.visitFunctionStmt(self)

class Return(Stmt):
    def __init__(self,keyword:Token,value:Expr):
        self.keyword=keyword
        self.value=value

    def accept(self,visitor):
        return visitor.visitReturnStmt(self)

class Class(Stmt):
     def __init__(self,name:Token,superclass:Variable,methods:list):
        self.name=name
        self.methods=methods
        self.superclass=superclass

     def accept(self,visitor):
        return visitor.visitClassStmt(self)







