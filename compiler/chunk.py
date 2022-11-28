from enum import Enum,auto,IntEnum
from collections import namedtuple
import value
from copy import deepcopy

#instruction set
class OpCode(Enum):
    OP_RETURN=0
    OP_CONSTANT=1 #need op+constant index 
    OP_NEGATE=2
    OP_ADD=3
    OP_SUBTRACT=4
    OP_MULTIPLY=5
    OP_DIVIDE=6
    OP_NIL=7
    OP_TRUE=8
    OP_FALSE=9
    OP_NOT=10
    OP_EQUAL=11
    OP_GREATER=12
    OP_LESS=13
    OP_PRINT=14
    OP_POP=15
    OP_DEFINE_GLOBAL=16
    OP_GET_GLOBAL=17
    OP_SET_GLOBAL=18
    OP_GET_LOCAL=19
    OP_SET_LOCAL=20
    OP_JUMP_IF_FALSE=21
    OP_JUMP=22
    OP_LOOP=23
    OP_CALL=24
    OP_CLOSURE=25
    OP_GET_UPVALUE=26
    OP_SET_UPVALUE=27
    OP_CLOSE_UPVALUE=28
        
class Chunk:
    __slots__ = ["code", "count","capacity","constants","lines"]
    def __init__(self,code:list=[],count:int=0,capacity:int=0,constants=value.ValueArray()) -> None:
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

def addConstant(chunk:Chunk,val:value.Value):
    value.writeValueArray(chunk.constants,val)
    return chunk.constants.count-1
    
    
    
    
    
    

    

    
    
    