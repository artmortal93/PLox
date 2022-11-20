from chunk import *
from enum import Enum
from value import *
from debug import *
from collections import deque
from compiler import *




#chunk is from outside 
#stack is VM own state
class VM:
    STACK_MAX=256
    def __init__(self) -> None:
        self.chunk=None
        self.ip=0 
        self.DEBUG_TRACE_EXECUTION=False
        self.stack=deque([None]*self.STACK_MAX)
        self.stackTop=0
        
vm=VM()
        
        
class InterpretResult(Enum):
    INTERPRET_OK=0
    INTERPRET_COMPILE_ERROR=1
    INTERPRET_RUNTIME_ERROR=2
        
def resetStack():
    global vm
    vm.stackTop=0 #just set to the begining of array
    
def initVM():
    global vm
    resetStack()
    
def freeVM():
    global vm
    pass

'''
push a value in stack of vm
'''
def push(value:Value):
    global vm
    vm.stack[vm.stackTop]=value 
    vm.stackTop+=1

def pop():
    global vm
    vm.stackTop-=1
    return vm.stack[vm.stackTop]    
    

def interpret(source:str)->InterpretResult:
    global vm
    chunk=initChunk()
    if not compile(source,chunk):
        freeChunk(chunk)
        return InterpretResult.INTERPRET_COMPILE_ERROR
    vm.chunk=chunk 
    vm.ip=0
    result=run()
    freeChunk(chunk)
    return result
    
    
def read_byte():
    global vm
    instruction=vm.chunk.code[vm.ip]
    vm.ip+=1
    return instruction

def read_constant():
    global vm
    return vm.chunk.constants.values[read_byte()]


def peek(distance:int):
    global vm 
    return vm.stack[vm.stackTop-1-distance]
    
def runtimeError(message,*args):
    global vm 
    print(message.format(*args))
    instruction=vm.ip-0-1
    line=vm.chunk.lines[instruction]
    print("[line {}] in script".format(line))
    resetStack()
    
def isFalsey(value:Value)->bool:
    return IS_NIL(value) or (IS_BOOL(value) and not AS_BOOL(value))

def run()->InterpretResult:
    global vm
    while True:
        if vm.DEBUG_TRACE_EXECUTION:
            print("       ",end='')
            for i in range(vm.stackTop):
                print("[{}]".format(vm.stack[i]),end='')
            print()
            disassembleInstruction(vm.chunk,vm.ip)
        instruction=read_byte()
        if instruction==OpCode.OP_RETURN:
            printValue(pop())
            print("")
            return InterpretResult.INTERPRET_OK
        elif instruction==OpCode.OP_CONSTANT:
            constant=read_constant()
            push(constant)
            printValue(constant)
            print('')
        elif instruction==OpCode.OP_NEGATE:
            if not IS_NUMBER(peek(0)):
                runtimeError("Opedand must be a number")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            val=-1*AS_NUMBER(pop())
            val=NUMBER_VAL(val)
            push(val)
        elif instruction==OpCode.OP_ADD:
            if not IS_NUMBER(peek(0)) and not IS_NUMBER(peek(1)):
                RuntimeError("Operands must be numbers")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            b=AS_NUMBER(pop())
            a=AS_NUMBER(pop())
            v=a+b
            push(NUMBER_VAL(v))
        elif instruction==OpCode.OP_DIVIDE:
            if not IS_NUMBER(peek(0)) and not IS_NUMBER(peek(1)):
                RuntimeError("Operands must be numbers")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            b=AS_NUMBER(pop())
            a=AS_NUMBER(pop())
            v=a/b
            push(NUMBER_VAL(v))
        elif instruction==OpCode.OP_MULTIPLY:
            if not IS_NUMBER(peek(0)) and not IS_NUMBER(peek(1)):
                RuntimeError("Operands must be numbers")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            b=AS_NUMBER(pop())
            a=AS_NUMBER(pop())
            v=a*b
            push(NUMBER_VAL(v))
        elif instruction==OpCode.OP_SUBTRACT:
            if not IS_NUMBER(peek(0)) and not IS_NUMBER(peek(1)):
                RuntimeError("Operands must be numbers")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            b=AS_NUMBER(pop())
            a=AS_NUMBER(pop())
            v=a-b
            push(NUMBER_VAL(v)) 
        elif instruction==OpCode.OP_NIL:
            push(NIL_VAL())
        elif instruction==OpCode.OP_TRUE:
            push(BOOL_VAL(True))
        elif instruction==OpCode.OP_FALSE:
            push(BOOL_VAL(False))  
        elif instruction==OpCode.OP_NOT:
            push(BOOL_VAL(isFalsey(pop())))    
        else:
            pass
        
