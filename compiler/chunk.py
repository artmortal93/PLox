from enum import Enum,auto,IntEnum
from collections import namedtuple
from value import *
from copy import deepcopy

#instruction set
class OpCode(Enum):
    OP_RETURN=auto()
    OP_CONSTANT=auto() #need op+constant index 
    OP_NEGATE=auto()
    OP_ADD=auto()
    OP_SUBTRACT=auto()
    OP_MULTIPLY=auto()
    OP_DIVIDE=auto()
    OP_NIL=auto()
    OP_TRUE=auto()
    OP_FALSE=auto()
    OP_NOT=auto()
        
class Chunk:
    __slots__ = ["code", "count","capacity","constants","lines"]
    def __init__(self,code:list=[],count:int=0,capacity:int=0,constants=ValueArray()) -> None:
        self.code=code
        self.count=count
        self.capacity=capacity
        self.constants=constants
        self.lines=[]
    
    
def initChunk():
    c=Chunk()
    return c

"""
byte:bytes to write
"""
def writeChunk(chunk:Chunk,byte,line:int):
    if chunk.capacity<chunk.count+1:
        oldCapacity=chunk.capacity
        chunk.capacity=growCapacity(oldCapacity)
        growArray(chunk,oldCapacity,growCapacity(oldCapacity))
    chunk.code[chunk.count]=byte
    chunk.lines[chunk.count]=line
    chunk.count+=1
        
def growCapacity(oldCapacity):
    if oldCapacity<8:
        return 8
    else:
        return oldCapacity*2
#may need refactor

def growArray(chunk,oldCapacity,newCapacity):
    tempLine=chunk.lines
    tempChunk=chunk.code
    tempCount=chunk.count
    chunk.code=[None]*newCapacity
    chunk.code[:tempCount]=tempChunk
    chunk.lines=[None]*newCapacity
    chunk.lines[:tempCount]=tempLine
    chunk.capacity=newCapacity

def freeChunk(chunk:Chunk):
    del chunk
    return Chunk([],0,0)

def addConstant(chunk:Chunk,value:Value):
    writeValueArray(chunk.constants,value)
    return chunk.constants.count-1
    
    
    
    
    
    

    

    
    
    