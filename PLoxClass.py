import PLoxCallable
from PLoxDef import *

class PLoxClass(PLoxCallable.LoxCallable):
    def __init__(self, name:str,superclass,methods):
        self.name=name
        self.methods=methods
        self.superclass=superclass

    def __str__(self):
        return self.name 

    def call(self,interpreter,arguments):
        instance=PLoxInstance(self)
        #find a user specific method init
        initializer=self.findMethod('init')
        if initializer is not None:
            initializer.bind(instance).call(interpreter,arguments)
        return instance

    def findMethod(self,name):
        m=self.methods.get(name)
        sm=None
        if self.superclass is not None:
            sm=self.superclass.findMethod(name)
        if m!=None:
            return m
        return sm

    def arity(self):
        initializer=self.findMethod('init')
        if initializer is None:
            return 0
        else:
            return initializer.arity()


class PLoxInstance:
    def __init__(self, klass:PLoxClass):
        self.klass=klass
        self.fields={}

    def __str__(self):
        return self.klass.name+" instance"

    def get(self,name:Token):
        if self.fields.get(name.lexeme) is not None:
            return self.fields[name.lexeme]
        method=self.klass.findMethod(name.lexeme)
        #bind this signature instance to function itself
        if method is not None:
            return method.bind(self)
        raise RunTimeError(name,"Undefined property:{}".format(name.lexeme))

    def set(self,name,value):
        self.fields[name.lexeme]=value





