from enum import Enum
import value
import debug
import chunk
from collections import deque
import compiler
import table
from copy import deepcopy


class CallFrame:
    def __init__(self) -> None:
        self.closure=None #the function it contains
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
        self.frames=[None]*self.FRAMES_MAX#call frames
        for i in range(self.FRAMES_MAX):
            self.frames[i]=CallFrame()
        self.frameCount=0
        self.openUpvalues=None #linked list of upvalue in everywhere
        self.grayCount=0
        self.grayCapacity=0
        self.grayStack=[]
        self.bytesAllocated=0
        self.nextGC=1024*1024
        self.initString=None
    
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
    vm.initString=value.copyString("init",4)
    defineNative("clock",clockNative)
    resetStack()
    
def freeVM():
    global vm
    vm.initString=None 
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
    closure=value.newClosure(function)
    pop()
    push(value.OBJ_VAL(closure))
    callValue(value.OBJ_VAL(closure),0)
    return run()
    
    
def read_byte():
    global vm
    #topmost frame
    curFrame=vm.frames[vm.frameCount-1]
    cur_ip=curFrame.ip
    #assert len(curFrame.closure.function.chunk.code)>cur_ip,curFrame.closure.function.chunk.code
    instruction=curFrame.closure.function.chunk.code[cur_ip]
    vm.frames[vm.frameCount-1].ip+=1
    return instruction

def read_constant():
    global vm
     #topmost frame
    curFrame=vm.frames[vm.frameCount-1]
    return curFrame.closure.function.chunk.constants.values[read_byte()]

def read_string():
    global vm
    val=value.AS_STRING(read_constant())
    return val

def read_short():
    global vm
    vm.frames[vm.frameCount-1].ip+=2
    curFrame=vm.frames[vm.frameCount-1]
    f=curFrame.closure.function.chunk.code[curFrame.ip-1]
    l=curFrame.closure.function.chunk.code[curFrame.ip-2]
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
    line=frame.closure.function.chunk.lines[instruction]
    print("[line {}] in script".format(line))
    for i in reversed(range(0,vm.frameCount)):
        frame=vm.frames[i]
        fun=frame.closure.function
        instruction=frame.ip-0-1
        info="[line {} ] in ".format(fun.chunk.lines[instruction])
        if fun.name is None:
            info+="script"
        else:
            info+=fun.name.chars+"()"
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
            #print("       ",end='')
            #for i in range(vm.stackTop):
                #print("[{}]".format(vm.stack[i]),end='')
            #    value.printValue(vm.stack[i])
            #print()
            debug.disassembleInstruction(frame.closure.function.chunk,frame.ip)
        instruction=read_byte()
        if instruction==chunk.OpCode.OP_RETURN:
            result=pop()
            vm.frameCount-=1
            if vm.frameCount==0:
                pop() #pop out main function
                return InterpretResult.INTERPRET_OK
            vm.stackTop=frame.slots
            push(result) #return value,we only discard the function var
            frame=vm.frames[vm.frameCount-1]
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
        elif instruction==chunk.OpCode.OP_GET_UPVALUE:
            slot=read_byte()
            #loc=frame.closure.upvalues[slot].location
            val=frame.closure.upvalues[slot].location
            push(val) #right?  
        elif instruction==chunk.OpCode.OP_SET_UPVALUE:
            slot=read_byte()
            frame.closure.upvalues[slot].location=peek(0)
        elif instruction==chunk.OpCode.OP_CLOSE_UPVALUE:
            #closeUpvalues(frame.slots) #we dont need this as python pass by ref semantics
            pop()
        elif instruction==chunk.OpCode.OP_GET_PROPERTY:
            if not value.IS_INSTANCE(peek(0)):
                runtimeError("Only instances have properties")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            instance=value.AS_INSTANCE(peek(0))
            name=read_string()
            val=None
            if table.tableGet(instance.fields,name)[0]==True:
                val=table.tableGet(instance.fields,name)[1].value
                #print("get val {}".format(val.asval.chars))
                pop() #the instance is at top if name.field is call
                push(val)#push the function
                continue
                #do not return, we continue
            tryBind=bindMethod(instance.klass,name)
            if tryBind==False:
                runtimeError("Undefined method {} in a Class".format(name.chars))
                return InterpretResult.INTERPRET_RUNTIME_ERROR 
            else:
                continue
            #runtimeError("Undefined Property {} in a Class".format(name.chars))
            #return InterpretResult.INTERPRET_RUNTIME_ERROR
        elif instruction==chunk.OpCode.OP_SET_PROPERTY:
            if not value.IS_INSTANCE(peek(1)):
                runtimeError("Only instances have properties")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            instance=value.AS_INSTANCE(peek(1))
            table.tableSet(instance.fields,read_string(),peek(0))
            val=pop()
            pop()
            push(val)
        elif instruction==chunk.OpCode.OP_GET_SUPER:
            name=read_string()
            superclass=value.AS_CLASS(pop()) #? how do it know
            if not bindMethod(superclass,name):
                return InterpretResult.INTERPRET_RUNTIME_ERROR
        elif instruction==chunk.OpCode.OP_METHOD:
            defineMethod(read_string())
        elif instruction==chunk.OpCode.OP_CLASS:
            push(value.OBJ_VAL(value.newClass(read_string())))
        elif instruction==chunk.OpCode.OP_CLOSURE:
            function=value.AS_FUNCTION(read_constant())
            closure=value.newClosure(function)
            push(value.OBJ_VAL(closure))
            for i in range(0,closure.upvalueCount):
                isLocal=read_byte()
                index=read_byte() #the index is the upvalue slot idx
                if isLocal:
                    #the magic is that you could always capture
                    #because the fun declataion order!
                    #index is the slot number of previous call stack, if local
                    #index is the idx of enclosing upvalue array, if not local
                    closure.upvalues[i]=captureUpvalue(frame.slots+index)
                else:
                    #the fun declaratinn go recursivly so you must get a value,because the former function get this first
                    closure.upvalues[i]=frame.closure.upvalues[index]
        elif instruction==chunk.OpCode.OP_INVOKE:
            method=read_string()
            argCount=read_byte()
            if not invoke(method,argCount):
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            frame=vm.frames[vm.frameCount-1]
        elif instruction==chunk.OpCode.OP_SUPER_INVOKE:
            method=read_string()
            argCount=read_byte()
            superclass=value.AS_CLASS(pop())
            if not invokeFromClass(superclass,method,argCount):
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            frame=vm.frames[vm.frameCount-1]
        else:
            pass
        
        
def invoke(name,argCount):
    reciever=peek(argCount)
    if not value.IS_INSTANCE(reciever):
        runtimeError("Only instances have methods")
        return False
    instance=value.AS_INSTANCE(reciever)
    res=table.tableGet(instance.fields,name)
    if res[0]==True:
        v=res[1]
        vm.stack[vm.stackTop-argCount-1]=v
        return callValue(v,argCount)
    return invokeFromClass(instance.klass,name,argCount)

def invokeFromClass(klass,name,argCount):
    res=table.tableGet(klass.methods,name)
    if res[0]==False:
        runtimeError("Undefined Property {}",name.chars)
        return False
    method=res[1].value
    return call(value.AS_CLOSURE(method),argCount)
        
def call(closure:value.ObjClosure,argCount:int):
    global vm 
    if argCount!=closure.function.arity:
        runtimeError("Expect arguments number {} but get {}".format(closure.function.arity,argCount))
        return False
    if vm.frameCount==256:
        runtimeError("Stack overflow")
        return False
    '''
    if vm.frameCount!=0:
        print("current top frame:{}".format(vm.frames[vm.frameCount-1].function.name.chars))
        print("upcoming frame:{}".format(function.name.chars))
        print("ought to empty frame:{}".format(vm.frames[vm.frameCount].function.name.chars))
    else:
        print("upcoming frame:{}".format(function.name.chars))
        print("ought to empty frame:{}".format(vm.frames[vm.frameCount].function.name.chars))
    '''    
    vm.frames[vm.frameCount].closure=closure
    vm.frames[vm.frameCount].ip=0
    vm.frames[vm.frameCount].slots=vm.stackTop-argCount-1 #slots point at the position of fun obj
    vm.frameCount+=1
    '''
    print("vm call function {} in call()".format(function.name.chars))
    for i in reversed(range(0,vm.frameCount)):
        print(vm.frames[i].function.name.chars,end=' ')
    print()
    '''
    return True
        
def callValue(callee:value.Value,argCount:int):
    if value.IS_OBJ(callee):
        t=value.OBJ_TYPE(callee)
        #this is redundant now
        #if t==value.ObjType.OBJ_FUNCTION:
        #    return call(value.AS_FUNCTION(callee),argCount)
        if t==value.ObjType.OBJ_NATIVE:
            native=value.AS_NATIVE(callee)
            arguments=[]
            for i in range(vm.stackTop-argCount,vm.stackTop):
                arguments.append(deepcopy(vm.stack[i]))
            argTuple=tuple(arguments)    
            res=native(argCount,argTuple)
            vm.stackTop-= argCount+1
            push(res)
            return True
        elif t==value.ObjType.OBJ_CLOSURE:
            return call(value.AS_CLOSURE(callee),argCount)
        elif t==value.ObjType.OBJ_CLASS:
            klass=value.AS_CLASS(callee)
            vm.stack[vm.stackTop-argCount-1]=value.OBJ_VAL(value.newInstance(klass))
            res=table.tableGet(klass.methods,vm.initString)
            if res[0] is True:
                return call(value.AS_CLOSURE(res[1].value),argCount)
            else:
                if argCount!=0:
                    runtimeError("Expected 0 argument for initalizer but got {}".format(argCount))
                    return False
            return True
        elif t==value.ObjType.OBJ_BOUND_METHOD:
            bound=value.AS_BOUND_METHOD(callee)
            vm.stack[vm.stackTop-argCount-1]=bound.reciever
            return call(bound.method,argCount)
        elif t==value.ObjType.OP_INHERIT:
            superclass=value.AS_CLASS(peek(0))
            subclass=value.AS_CLASS(peek(1))
            if not value.IS_CLASS(superclass):
                runtimeError("Super class must be a class")
                return InterpretResult.INTERPRET_RUNTIME_ERROR
            #copy and cover, OP_INHERIT IS before class declaration, so no shadowing
            table.tableAddAll(superclass.methods,subclass.methods)
            pop()
        else:
            pass 
    runtimeError("can only call function and classes")
    return False
        
def defineNative(name:str,fun):
    push(value.OBJ_VAL(value.copyString(name,len(name))))
    push(value.OBJ_VAL(value.newNative(fun)))
    global vm
    table.tableSet(vm.globals,value.AS_STRING(vm.stack[0]),vm.stack[1])
    pop()
    pop()
    

def defineMethod(name:value.ObjString):
    method=peek(0)
    klass=value.AS_CLASS(peek(1))
    table.tableSet(klass.methods,name,method)
    pop() 
    
    
def bindMethod(klass,name):
    method=None 
    res=table.tableGet(klass.methods,name)    
    if res[0]==False:
        runtimeError("Undefined method property {}".format(name.chars))
        return False 
    method=res[1].value
    bound=value.newBoundMethod(peek(0),value.AS_CLOSURE(method))
    pop()
    push(value.OBJ_VAL(bound))
    return True
    
def clockNative(argCount,*args):
    import time
    return value.NUMBER_VAL(time.time())


def captureUpvalue(local):
    global vm 
    prevUpvalue=None
    upvalue=vm.openUpvalues
    while upvalue!=None and upvalue!=vm.stack[local]:
        prevUpvalue=upvalue
        upvalue=upvalue.next
    if upvalue!=None and upvalue==local:
        return upvalue 
    createdUpvalue=value.newUpvalue(vm.stack[local])
    createdUpvalue.next=upvalue
    if prevUpvalue==None:
        vm.openUpvalues=createdUpvalue
    else:
        prevUpvalue.next=createdUpvalue    
    return createdUpvalue

#in clox this is used to de-ref the abs stack pointer and store things in heap
#redundant in py,just for ref to book usage
#we dont need this because we capture by reference,but not a single stack slot pointer
def closeUpvalues(last):
    global vm
    while vm.openUpvalues is not None and vm.openUpvalues.location!=last:
        upvalue=vm.openUpvalues
        upvalue.closed=upvalue.location
        upvalue.location=upvalue.closed
        vm.openUpvalues=upvalue.next
    
