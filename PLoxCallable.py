from abc import ABC
import PLoxInterpreter
import time
from PLoxDef import *
import PLoxEnvironment

class LoxCallable(ABC):
    def call(self,interpreter,arguments):
        pass

    def arity(self):
        pass

class ClockCallable(LoxCallable):
    def call(self, interpreter, arguments):
        return float(time.time()) 

    def arity(self):
        return 0

    def __str__(self)->str:
        return "<native fn>"

class LoxFunction(LoxCallable):
    def __init__(self,declaration:Function):
        #store whole stmt object,this is used for visit Function Node stmt
        super().__init__()
        self.declaration=declaration #a whole stmt object

    #argument are true value, param are argument placeholder
    def call(self,interpreter,arguments:list):
        env=PLoxEnvironment.environment(interpreter.globalEnv)
        for i in range(len(self.declaration.params)):
            env.define(self.declaration.params[i].lexeme,arguments[i])
        #define local variable for args
        try:
            interpreter.executeBlock(self.declaration.body,env)
            return None
        except ReturnException as e:
            return e.value
        

    def arity(self):
        return len(self.declaration.params)

    def __str__(self)->str:
        return "<fn {}>".format(self.declaration.name.lexeme)






    
