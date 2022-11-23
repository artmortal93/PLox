from enum import Enum
import value
import debug
import chunk
from collections import deque
import compiler
import table

#chunk is from outside 
#stack is VM own state
class VM:
    STACK_MAX=256
    def __init__(self) -> None:
        self.chunk=None
        self.ip=0 
        self.DEBUG_TRACE_EXECUTION=False
        self.stack=deque([None]*self.STACK_MAX)
        self.objects=deque() #heap for large objects(DEPRECATED)
        self.strings=table.Table() #able to find all the string it created
        self.stackTop=0
        self.globals=table.Table() #global var table

    
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
    table.initTable(vm.strings)
    table.initTable(vm.globals)
    resetStack()
    
def freeVM():
    global vm
    table.freeTable(vm.strings)
    table.freeTable(vm.globals)
    freeObjects()

def freeObjects():
    global vm 
    vm.objects.clear()

'''
push a value in stack of vm
'''
def push(val:value.Value):
    global vm
    vm.stack[vm.stackTop]=val 
    vm.stackTop+=1

def pop():
    global vm
    vm.stackTop-=1
    return vm.stack[vm.stackTop]    
    

def interpret(source:str)->InterpretResult:
    global vm
    c=chunk.initChunk()
    if not compiler.compile(source,c):
        chunk.freeChunk(c)
        return InterpretResult.INTERPRET_COMPILE_ERROR
    vm.chunk=c 
    vm.ip=0
    result=run()
    chunk.freeChunk(c)
    return result
    
    
def read_byte():
    global vm
    instruction=vm.chunk.code[vm.ip]
    vm.ip+=1
    return instruction

def read_constant():
    global vm
    return vm.chunk.constants.values[read_byte()]

def read_string():
    global vm
    val=value.AS_STRING(read_constant())
    return val


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
    
def isFalsey(val:value.Value)->bool:
    return value.IS_NIL(val) or (value.IS_BOOL(val) and not value.AS_BOOL(val))

def concatenate():
    global vm 
    b=value.AS_CSTRING(pop())
    a=value.AS_CSTRING(pop())
    length=len(a)+len(b)
    c=a+b
    result=value.takeString(c,length)
    push(value.OBJ_VAL(result))
    

def run()->InterpretResult:
    global vm
    while True:
        if vm.DEBUG_TRACE_EXECUTION:
            print("       ",end='')
            for i in range(vm.stackTop):
                print("[{}]".format(vm.stack[i]),end='')
            print()
            debug.disassembleInstruction(vm.chunk,vm.ip)
        instruction=read_byte()
        if instruction==chunk.OpCode.OP_RETURN:
            return InterpretResult.INTERPRET_OK
        elif instruction==chunk.OpCode.OP_CONSTANT:
            constant=read_constant()
            push(constant)
            #printValue(constant)
            #print('')
        elif instruction==chunk.OpCode.OP_NEGATE:
            if not value.IS_NUMBER(peek(0)):
                runtimeError("Opedand must be a number")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            val=-1*value.AS_NUMBER(pop())
            val=value.NUMBER_VAL(val)
            push(val)
        elif instruction==chunk.OpCode.OP_ADD:
            if value.IS_STRING(peek(0)) and value.IS_STRING(peek(1)):
                concatenate()  
            elif value.IS_NUMBER(peek(0)) and value.IS_NUMBER(peek(1)):
                b=value.AS_NUMBER(pop())
                a=value.AS_NUMBER(pop())
                v=a+b
                push(value.NUMBER_VAL(v))
            else:
                RuntimeError("Operands must be numbers or strings")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
        elif instruction==chunk.OpCode.OP_DIVIDE:
            if not value.IS_NUMBER(peek(0)) and not value.IS_NUMBER(peek(1)):
                RuntimeError("Operands must be numbers")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            b=value.AS_NUMBER(pop())
            a=value.AS_NUMBER(pop())
            v=a/b
            push(value.NUMBER_VAL(v))
        elif instruction==chunk.OpCode.OP_MULTIPLY:
            if not value.IS_NUMBER(peek(0)) and not value.IS_NUMBER(peek(1)):
                RuntimeError("Operands must be numbers")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            b=value.AS_NUMBER(pop())
            a=value.AS_NUMBER(pop())
            v=a*b
            push(value.NUMBER_VAL(v))
        elif instruction==chunk.OpCode.OP_SUBTRACT:
            if not value.IS_NUMBER(peek(0)) and not value.IS_NUMBER(peek(1)):
                RuntimeError("Operands must be numbers")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            b=value.AS_NUMBER(pop())
            a=value.AS_NUMBER(pop())
            v=a-b
            push(value.NUMBER_VAL(v)) 
        elif instruction==chunk.OpCode.OP_NIL:
            push(value.NIL_VAL())
        elif instruction==chunk.OpCode.OP_TRUE:
            push(value.BOOL_VAL(True))
        elif instruction==chunk.OpCode.OP_FALSE:
            push(value.BOOL_VAL(False))  
        elif instruction==chunk.OpCode.OP_NOT:
            push(value.BOOL_VAL(isFalsey(pop())))
        elif instruction==chunk.OpCode.OP_EQUAL:
            b=pop()
            a=pop()
            push(value.BOOL_VAL(value.valuesEqual(a,b)))
        elif instruction==chunk.OpCode.OP_GREATER:
            if not value.IS_NUMBER(peek(0)) and not value.IS_NUMBER(peek(1)):
                RuntimeError("Operands must be numbers")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            b=value.AS_NUMBER(pop())
            a=value.AS_NUMBER(pop())
            v=a>b
            push(value.BOOL_VAL(v)) 
        elif instruction==chunk.OpCode.OP_LESS:
            if not value.IS_NUMBER(peek(0)) and not value.IS_NUMBER(peek(1)):
                RuntimeError("Operands must be numbers")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            b=value.AS_NUMBER(pop())
            a=value.AS_NUMBER(pop())
            v=a<b
            push(value.BOOL_VAL(v)) 
        elif instruction==chunk.OpCode.OP_PRINT:
            value.printValue(pop())
            print("")  
        elif instruction==chunk.OpCode.OP_POP:
            pop()      
        elif instruction==chunk.OpCode.OP_DEFINE_GLOBAL:
            name=read_string() #get objString object
            table.tableSet(vm.globals,name,peek(0)) #peek is value in stack
            pop()
        elif instruction==chunk.OpCode.OP_GET_GLOBAL:
            name=read_string()
            res=table.tableGet(vm.globals,name)#return entries
            if res[0] is False:
                runtimeError("Undefined variable {}",name.chars)
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            push(res[1].value)
        elif instruction==chunk.OpCode.OP_SET_GLOBAL:
            name=read_string()
            if table.tableSet(vm.globals,name,peek(0)):
                table.tableDelete(vm.globals,name)
                runtimeError("Undefined variable {}".format(name.chars))
                return InterpretResult.INTERPRET_RUNTIME_ERROR
        elif instruction==chunk.OpCode.OP_GET_LOCAL:
            slot=read_byte()
            push(vm.stack[slot])
        elif instruction==chunk.OpCode.OP_SET_LOCAL:
            slot=read_byte()
            vm.stack[slot]=peek(0)
        else:
            pass
        
