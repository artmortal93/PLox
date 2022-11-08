from PLoxDef import *
import PLox

class environment:
    def __init__(self,enclosing=None):
        self.values={}
        self.enclosing=enclosing #outer environment,which is bigger,most outer has none

    def define(self,name:str,value):
        self.values[name]=value

    def get(self, name:Token):
        if self.values.get(name.lexeme,"Not Registered") != "Not Registered":
            return self.values.get(name.lexeme)
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise RunTimeError(name,"Undefined variable '"+name.lexeme+"'.")
    
    def assign(self,name,value):
        if self.values.get(name.lexeme,"Not Registered") != "Not Registered":
            self.values[name.lexeme]=value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name,value)
            return
        raise RunTimeError(name,"Undefined variable '"+name.lexeme+"'.")