from enum import Enum
import value
import debug
import chunk
from collections import deque
import compiler
import table


class CallFrame:
    def __init__(self) -> None:
        self.function=None #the function it contains
        self.slots=None #the first usable vm value stack pointer it can use
        self.ip=None #record the ip of the caller so we can jump to

#chunk is from outside 
#stack is VM own state
class VM:
    STACK_MAX=1024
    FRAMES_MAX=64
    def __init__(self) -> None:
        self.chunk=None
        self.ip=0 #has no use and replaced by callframe.ip
        self.DEBUG_TRACE_EXECUTION=False
        self.stack=deque([None]*self.STACK_MAX)
        self.objects=deque() #heap for large objects(DEPRECATED)
        self.strings=table.Table() #able to find all the string it created
        self.stackTop=0
        self.globals=table.Table() #global var table
        self.frames=deque([CallFrame()]*self.FRAMES_MAX)#call frames
        self.frameCount=0

    
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
    function=compiler.compile(source)
    if function is None:
        return InterpretResult.INTERPRET_COMPILE_ERROR
    #vm.frames[vm.frameCount].function=function
    #vm.frames[vm.frameCount].ip=0
    #slots only indicate the current call frame's start position
    #vm.frames[vm.frameCount].slots=0#vm.stack
    #vm.frameCount+=1
    push(value.OBJ_VAL(function))
    callValue(value.OBJ_VAL(function),0)
    return run()
    
    
def read_byte():
    global vm
    #topmost frame
    curFrame=vm.frames[vm.frameCount-1]
    cur_ip=curFrame.ip
    instruction=curFrame.function.chunk.code[cur_ip]
    vm.frames[vm.frameCount-1].ip+=1
    return instruction

def read_constant():
    global vm
     #topmost frame
    curFrame=vm.frames[vm.frameCount-1]
    return curFrame.function.chunk.constants.values[read_byte()]

def read_string():
    global vm
    val=value.AS_STRING(read_constant())
    return val

def read_short():
    global vm
    vm.frames[vm.frameCount-1].ip+=2
    curFrame=vm.frames[vm.frameCount-1]
    f=curFrame.function.chunk.code[curFrame.ip-1]
    l=curFrame.function.chunk.code[curFrame.ip-2]
    n=(l<<8) | f 
    return n


def peek(distance:int):
    global vm 
    return vm.stack[vm.stackTop-1-distance]
    
def runtimeError(message,*args):
    global vm 
    print(message.format(*args))
    frame=vm.frames[vm.frameCount-1]
    instruction=frame.ip-0-1
    line=frame.function.chunk.lines[instruction]
    print("[line {}] in script".format(line))
    for i in reversed(range(0,vm.frameCount)):
        frame=vm.frames[i]
        fun=frame.function
        instruction=frame.ip-0-1
        info="[line {} ] in ".format(fun.chunk.lines[instruction])
        if fun.name is None:
            info+="script"
        else:
            info+=fun.name.chars
        print(info)    
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
    frame=vm.frames[vm.frameCount-1] #point to the current frame
    while True:
        if vm.DEBUG_TRACE_EXECUTION:
            print("       ",end='')
            for i in range(vm.stackTop):
                print("[{}]".format(vm.stack[i]),end='')
            print()
            debug.disassembleInstruction(frame.function.chunk,frame.ip)
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
                runtimeError("Operands must be numbers or strings")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
        elif instruction==chunk.OpCode.OP_DIVIDE:
            if not value.IS_NUMBER(peek(0)) and not value.IS_NUMBER(peek(1)):
                runtimeError("Operands must be numbers")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            b=value.AS_NUMBER(pop())
            a=value.AS_NUMBER(pop())
            v=a/b
            push(value.NUMBER_VAL(v))
        elif instruction==chunk.OpCode.OP_MULTIPLY:
            if not value.IS_NUMBER(peek(0)) and not value.IS_NUMBER(peek(1)):
                runtimeError("Operands must be numbers")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            b=value.AS_NUMBER(pop())
            a=value.AS_NUMBER(pop())
            v=a*b
            push(value.NUMBER_VAL(v))
        elif instruction==chunk.OpCode.OP_SUBTRACT:
            if not value.IS_NUMBER(peek(0)) and not value.IS_NUMBER(peek(1)):
                runtimeError("Operands must be numbers")
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
                runtimeError("Operands must be numbers")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            b=value.AS_NUMBER(pop())
            a=value.AS_NUMBER(pop())
            v=a>b
            push(value.BOOL_VAL(v)) 
        elif instruction==chunk.OpCode.OP_LESS:
            if not value.IS_NUMBER(peek(0)) and not value.IS_NUMBER(peek(1)):
                runtimeError("Operands must be numbers")
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
            #push(frame.slots[slot])
            push(vm.stack[frame.slots+slot])
        elif instruction==chunk.OpCode.OP_SET_LOCAL:
            slot=read_byte()
            vm.stack[frame.slots+slot]=peek(0)
            #frame.slots[slot]=peek(0)
        elif instruction==chunk.OpCode.OP_JUMP_IF_FALSE:
            offset=read_short()
            if isFalsey(peek(0)):
                frame.ip+=offset
        elif instruction==chunk.OpCode.OP_JUMP:
            offset=read_short()
            frame.ip+=offset
        elif instruction==chunk.OpCode.OP_LOOP:
            offset=read_short()
            frame.ip-=offset
        elif instruction==chunk.OpCode.OP_CALL:
            #in this time the stack have
            #funObj arg1 arg2 arg3
            argCount=read_byte()
            if not callValue(peek(argCount),argCount):
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            #recover frame pointer because we get a new top call stack 
            frame=vm.frames[vm.frameCount-1]
        else:
            pass
        
def call(function:value.ObjFunction,argCount:int):
    global vm 
    if argCount!=function.arity:
        runtimeError("Expect arguments number {} but get {}".format(function.arity,argCount))
        return False
    if vm.frameCount==256:
        runtimeError("Stack overflow")
        return False
    frame=vm.frames[vm.frameCount]
    previousFrame=vm.frames[vm.frameCount-1]
    assert previousFrame is not None 
    vm.frames[vm.frameCount].function=function
    vm.frames[vm.frameCount].ip=0
    vm.frames[vm.frameCount].slots=vm.stackTop-argCount-1 #slots point at the position of fun obj
    vm.frameCount+=1
    return True
        
def callValue(callee:value.Value,argCount:int):
    if value.IS_OBJ(callee):
        t=value.OBJ_TYPE(callee)
        if t==value.ObjType.OBJ_FUNCTION:
            return call(value.AS_FUNCTION(callee),argCount)
        else:
            pass 
    runtimeError("can only call function and classes")
    return False
        
        
