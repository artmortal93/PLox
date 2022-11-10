from PLoxDef import *
import PLoxInterpreter
from collections import deque
import PLox

class Resolver(Visitor,StmtVisitor):
    """description of class"""
    def __init__(self,interpreter):
        super().__init__()
        self.interpreter=interpreter
        self.scopes=deque() #local only stack,if not found , must be global
        self.currentFunction=FunctionType.NONE
        self.currentClass=ClassType.NONE

    def visitBlockStmt(self, stmt:Block):
        self.beginScope()
        self.resolve(stmt.statments)
        self.endScope()
        return None

    #declare a var
    def visitVarStmt(self,stmt:Var):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)
        return None

    def visitFunctionStmt(self,stmt:Function):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolveFunction(stmt,FunctionType.FUNCTION)
        return None

    def visitExpressionStmt(self, stmt:Expression):
        self.resolve(stmt.expression)
        return None

    def visitIfStmt(self, stmt:If):
        self.resolve(stmt.condition)
        self.resolve(stmt.thenBranch)
        if stmt.elseBranch !=None:
            self.resolve(stmt.elseBranch)
        return None

    def visitPrintStmt(self, stmt:Print):
        self.resolve(stmt.expression)
        return None

    def visitReturnStmt(self, stmt:Return):
        if self.currentFunction == FunctionType.NONE:
            PLox.PLox.error(stmt.keyword,"Cant return from top level code")
        if stmt.value is not None:
            if self.currentFunction == FunctionType.INITIALIZER:
                PLox.PLox.error(stmt.keyword,"Cant return value from an initializer")
            self.resolve(stmt.value)
        return None

    def visitWhileStmt(self, stmt:While):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
        return None

    #this is always a keyword hint a outside scope for method body, so need extra scope
    def visitClassStmt(self, stmt:Class):
        enclosingClass=self.currentClass
        self.currentClass=ClassType.CLASS
        self.declare(stmt.name)
        self.define(stmt.name)
        if stmt.superclass is not None and stmt.name.lexeme==stmt.superclass.name.lexeme:
            PLox.PLox.error(stmt.superclass.name,"A class can not inherit from itself")
        if stmt.superclass is not None:
            self.currentClass=ClassType.SUBCLASS
            self.resolve(stmt.superclass)
        if stmt.superclass is not None:
            self.beginScope()
            self.scopes[-1]["super"]=True
        self.beginScope()
        self.scopes[-1]["this"]=True
        for m in stmt.methods:
            declaration=FunctionType.METHOD
            if m.name.lexeme=="init":
                declaration=FunctionType.INITIALIZER
            self.resolveFunction(m,declaration)
        self.endScope()
        if stmt.superclass is not None:
            self.endScope()
        self.currentClass=enclosingClass
        return None

    #assess a var
    def visitVariableExpr(self, expr:Variable):
        if len(self.scopes)!=0 and self.scopes[-1].get(expr.name.lexeme) is False:
            PLox.PLox.error(expr.name,"Cant read local var without initalizer.")
        self.resolveLocal(expr,expr.name)
        return None

    def visitAssignExpr(self,expr:Assign):
        self.resolve(expr.value)
        self.resolveLocal(expr,expr.name)
        return None

    def visitBinaryExpr(self,expr:Binary):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    def visitCallExpr(self,expr:Call):
        self.resolve(expr.callee)
        for argument in expr.arguments:
            self.resolve(argument)
        return None

    def visitGroupingExpr(self, expr:Grouping):
        self.resolve(expr.expression)
        return None

    def visitLiteralExpr(self, expr:Literal):
        return None

    def visitLogicalExpr(self,expr:Logical):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    def visitUnaryExpr(self,expr:Unary):
        self.resolve(expr.right)
        return None

    def visitGetExpr(self, expr:Get):
        self.resolve(expr.obj)
        return None

    def visitSetExpr(self, expr:Set):
        self.resolve(expr.value)
        self.resolve(expr.obj)
        return None

    def visitThisExpr(self,expr:This):
        if self.currentClass==ClassType.NONE:
            PLox.PLox.error(expr.keyword,"Cant use this outside of a class")
            return None
        self.resolveLocal(expr,expr.keyword)
        return None

    def visitSuperExpr(self,expr:Super):
        if self.currentClass!=ClassType.SUBCLASS:
            PLox.PLox.error(expr.keyword,"Cant use super with no subclass")
        self.resolveLocal(expr,expr.keyword)
        return None

    def resolveLocal(self,expr,name):
        length=len(self.scopes)
        for i in range(length-1,-1,-1):#traverse the stack from top
            if self.scopes[i].get(name.lexeme) is not None:
                self.interpreter.resolve(expr,length-1-i) #return which stack level we found the var
                return
        #else assume global variable
    
    #unlike runtime,declare a function immediately run the body and bind the params
    def resolveFunction(self,function:Function,type:FunctionType):
        enclosingFunction=self.currentFunction
        currentFunction=type
        self.beginScope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.endScope()
        self.currentFunction=enclosingFunction


    def resolve(self,statment):
        if isinstance(statment,list):
            for s in statment:
                self.resolve(s)
        elif isinstance(statment,Stmt):
            statment.accept(self)
        elif isinstance(statment,Expr):
            statment.accept(self)
        else:
            pass

    def declare(self,name:Token):
        if len(self.scopes)==0: #must be global
            return
        scope=self.scopes[-1] #peek the scope
        if scope.get(name.lexeme) is not None:
            PLox.PLox.error(name,"Variable is already defined in this scope")
        scope[name.lexeme]=False #means we are not ready to solve the var yet

    def define(self,name:Token):
        if len(self.scopes)==0: #must be global
            return
        scope=self.scopes[-1]
        scope[name.lexeme]=True


    def beginScope(self):
        self.scopes.append(dict())

    def endScope(self):
        self.scopes.pop()




  




    


