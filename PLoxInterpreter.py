from PLoxDef import *
import PLox

class PLoxInterpreter(Visitor):
    """description of class"""
    def __init__(self):
        super().__init__()

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

    def evaluate(self, expr:Expr):
        return expr.accept(self)

    def isTruthy(self,val):
        if val is None:
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

    #public interface
    def interpret(self,expression:Expr):
        try:
            val=self.evaluate(expression)
            print(self.stringify(val))
        except RunTimeError as e:
            PLox.PLox.runtimeError(e)
