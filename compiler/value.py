from typing import *
from enum import IntEnum,Enum
import chunk


class ValueType(IntEnum):
    VAL_BOOL=0
    VAL_NIL=1
    VAL_NUMBER=2
    
class Value:
    def __init__(self,type:ValueType,asval):
        self.asval=asval #union as double/boolean
        self.type=type
        
        
def IS_BOOL(value:Value):
    return value.type==ValueType.VAL_BOOL 

def IS_NUMBER(value:Value):
    return value.type==ValueType.VAL_NUMBER

def IS_NIL(value:Value):
    return value.type==ValueType.VAL_NIL

def AS_BOOL(value:Value):
    return value.asval

def AS_NUMBER(value:Value):
    return value.asval

#promoter a native C value to clox value        
def BOOL_VAL(value):
    value=Value(ValueType.VAL_BOOL,value)
    return value
    
def NIL_VAL():
    value=Value(ValueType.VAL_NIL,0)
    return value
   
def NUMBER_VAL(value):
    value=Value(ValueType.VAL_NUMBER,value)
    return value
    

#represent constant pool of binary exe 
class ValueArray:
    __slots__ = ["values", "count","capacity"]
    def __init__(self,values=[],count=0,capacity=0) -> None:
        self.capacity=capacity
        self.count=count 
        self.values=[]
        
def initValueArray():
    return ValueArray()

def writeValueArray(array:ValueArray,value:Value):
    if array.capacity<array.count+1:
        oldCapacity=array.capacity
        array.capacity=chunk.growCapacity(oldCapacity)
        temp_val=array.values 
        temp_count=array.count 
        array.values=[None]*array.capacity
        array.values[0:temp_count]=temp_val
    array.values[array.count]=value
    array.count+=1
        
    
def freeValueArray(array,value:Value):
    del array  
    return ValueArray([],0,0)

def printValue(value:Value):
    if value.type==ValueType.VAL_NUMBER:
        print("{}".format(AS_NUMBER(value)),end=' ')
    elif value.type==ValueType.VAL_NIL:
        print("nil")
    elif value.type==ValueType.VAL_BOOL:
        print("TRUE" if AS_BOOL(value) else "FALSE")
    
    


        
    
        
        
