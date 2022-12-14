from PLoxDef import *
from PLoxCallable import *
from PLoxClass import *
import PLox
import PLoxEnvironment

class Interpreter(Visitor,StmtVisitor):
    """description of class"""
    globalEnv=PLoxEnvironment.environment(None)
    def __init__(self):
        super().__init__()
        self.environment=self.globalEnv
        self.locals=dict()
        self.globalEnv.define("clock",ClockCallable())
        

    #Seperate Expr and Stmt




    def visitLiteralExpr(self, expr:Literal):
        return expr.value

    def visitBinaryExpr(self, expr:Binary):
        left=self.evaluate(expr.left)
        right=self.evaluate(expr.right)
        t=expr.operator.type
        if t==TokenType.MINUS:
            self.checkNumberOperands(expr.operator,left,right)
            return float(left)-float(right)
        elif t==TokenType.PLUS:
            if type(left) is float and type(right) is float:
                return float(left)+float(right)
            elif type(left) is str and type(right) is str:
                return str(left)+str(right)
            else:
                raise RunTimeError(expr.operator,"Operands must be two numbers or two strings")
        elif t==TokenType.SLASH:
            self.checkNumberOperands(expr.operator,left,right)
            return float(left)/float(right)
        elif t==TokenType.STAR:
            self.checkNumberOperands(expr.operator,left,right)
            return float(left)*float(right)
        elif t==TokenType.GREATER:
            self.checkNumberOperands(expr.operator,left,right)
            return float(left)>float(right)
        elif t==TokenType.GREATER_EQUAL:
            self.checkNumberOperands(expr.operator,left,right)
            return float(left)>=float(right)
        elif t==TokenType.LESS:
            self.checkNumberOperands(expr.operator,left,right)
            return float(left)<float(right)
        elif t==TokenType.LESS_EQUAL:
            self.checkNumberOperands(expr.operator,left,right)
            return float(left)<=float(right)
        elif t==TokenType.BANG_EQUAL:
            return not self.isEqual(left,right)
        elif t==TokenType.EQUAL_EQUAL:
            return self.isEqual(left,right)
        return None

    def visitGroupingExpr(self, expr:Grouping):
        return self.evaluate(expr.expression)

    def visitUnaryExpr(self, expr:Unary):
        rightVal=self.evaluate(expr.right)
        t=expr.operator.type
        if t==TokenType.MINUS:
            return -1.0*float(rightVal)
        if t==TokenType.BANG:
            return not self.isTruthy(rightVal)
        return None

    #change to resolver version
    def visitVariableExpr(self, expr:Variable):
        #return self.environment.get(expr.name)
        return self.lookUpVariable(expr.name,expr) 

    #change to resolver version
    def visitAssignExpr(self,expr:Assign):
        value=self.evaluate(expr.value)
        distance=self.locals.get(expr)
        if distance is not None:
            self.environment.assignAt(distance,expr.name,value)
        else:
            self.globalEnv.assign(expr.name,value)
        return value

    def visitLogicalExpr(self,expr:Logical):
        left=self.evaluate(expr.left)
        if expr.operator.type==TokenType.OR:
            if self.isTruthy(left):
                return left
            else:
                if not self.isTruthy(left):
                    return left
        return self.evaluate(expr.right)

    def visitCallExpr(self, expr:Call):
        callee=self.evaluate(expr.callee) #return PloxCallable object stored
        arguments=[]
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        if not isinstance(callee,LoxCallable):
            raise RunTimeError(expr.paren,"can only call function and classes")
        function=callee #cast to LoxCallable
        if len(arguments) != function.arity():
            raise RuntimeError(expr.paren,"Expected {} arguments but got {}.".format(function.arity(),len(arguments)))
        return function.call(self,arguments)

    def visitGetExpr(self, expr:Get):
        object=self.evaluate(expr.obj)
        if isinstance(object,PLoxInstance):
            return object.get(expr.name)
        raise RunTimeError(expr.name,"Only instances have properties")

    def visitSetExpr(self,expr:Set):
        object=self.evaluate(expr.obj)
        if not isinstance(object,PLoxInstance):
            raise RunTimeError(expr.name,"Only instances have properties")
        value=self.evaluate(expr.value)
        object.set(expr.name,value)
        return value

    def visitThisExpr(self,expr:This):
        return self.lookUpVariable(expr.keyword,expr)

    def visitSuperExpr(self,expr:Super):
        distance=self.locals.get(expr)
        superclass=self.environment.getAt(distance,"super")
        obj=self.environment.getAt(distance-1,"this")
        method=superclass.findMethod(expr.method.lexeme)
        if method is None:
            raise RunTimeError(expr.method,"Undefined propety {} in super".format(expr.method.lexeme))
        return method.bind(obj)
            
    #Seperate Expr and Stmt


    def visitExpressionStmt(self, stmt:Expression):
        self.evaluate(stmt.expression)
        return None 

    def visitPrintStmt(self, stmt:Print):
        value=self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visitVarStmt(self, stmt:Var):
        value=None
        if stmt.initializer is not None:
            value=self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme,value)
        return None

    def visitBlockStmt(self, stmt:Block):
        inner_env=PLoxEnvironment.environment(self.environment)#creat a inner env
        #fire it then forget it
        self.executeBlock(stmt.statments,inner_env)
        return None

    def visitIfStmt(self, stmt:If):
        if self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)
        elif stmt.elseBranch is not None:
            self.execute(stmt.elseBranch)
        return None

    def visitWhileStmt(self,stmt:While):
        while self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        return None

    def visitFunctionStmt(self, stmt:Function):
        function=LoxFunction(stmt,self.environment,False) #record outer environment
        self.environment.define(stmt.name.lexeme,function)
        return None

    def visitReturnStmt(self,stmt:Return):
        value=None
        if(stmt.value!=None):
            value=self.evaluate(stmt.value)
        raise ReturnException(value)
    
    def visitClassStmt(self,stmt:Class):
        superclass=None
        if stmt.superclass is not None:
            superclass=self.evaluate(stmt.superclass)
            if not isinstance(superclass,PLoxClass):
                raise RunTimeError(stmt.superclass.name,"super class must be class")
        self.environment.define(stmt.name.lexeme,None)
        #create environment for super
        if stmt.superclass is not None:
            self.environment=PLoxEnvironment.environment(self.environment)
            self.environment.define("super",superclass)
        methods={}
        for m in stmt.methods:
            isInit=m.name.lexeme == "init"
            func=LoxFunction(m,self.environment,isInit)
            methods[m.name.lexeme]=func
        #class contain methods dict
        klass=PLoxClass(stmt.name.lexeme,superclass,methods)
        if stmt.superclass is not None:
            self.environment=self.environment.enclosing
        self.environment.assign(stmt.name,klass)
        return None



    #Seperate Expr and Stmt
    


    def evaluate(self, expr:Expr):
        return expr.accept(self)

    def isTruthy(self,val):
        if val is None: #For nil case
            return False
        if type(val) is bool:
            return bool(val)
        return True

    def isEqual(self,a,b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a==b
    #this support multiple bracking with saving previous, and current environment
    def executeBlock(self,statments:list,env):
        previous=self.environment
        try:
            self.environment=env #replace with new env,whihc is inner env
            for s in statments:
                self.execute(s)
        finally:
            self.environment=previous

    def checkNumberOperands(self,operator, *operands):
        statusOk=True
        for operand in operands:
            if type(operand) is not float:
                statusOk=False
        if statusOk is False:
            raise RunTimeError(operator,"Operand must be a number")

    def stringify(self,obj)->str:
        if obj is None:
            return "nil"
        if type(obj) is float:
            text=str(obj)
            if text.endswith(".0"):
                text=text[0:len(text)-2]
            return text
        return str(obj)

    def lookUpVariable(self,name:Token,expr:Expr):
        distance=self.locals.get(expr)
        if distance is not None:
            return self.environment.getAt(distance,name.lexeme)
        else:
            return self.globalEnv.get(name)


    #public interface
    def interpret(self,statments:list):
        try:
            for statment in statments:
                self.execute(statment)
        except RunTimeError as e:
            PLox.PLox.runtimeError(e)

    def execute(self, stmt:Stmt):
        stmt.accept(self) 

    def resolve(self, expr:Expr, depth:int):
        self.locals[expr]=depth

        


