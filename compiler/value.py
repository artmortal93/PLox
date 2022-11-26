from enum import IntEnum,Enum
from copy import deepcopy


class ValueType(IntEnum):
    VAL_BOOL=0
    VAL_NIL=1
    VAL_NUMBER=2
    VAL_OBJ=3
    
class Value:
    def __init__(self,type:ValueType,asval):
        self.asval=asval #union as double/boolean/obj in c, we directly store in value itself,stop stupid pointer magic 
        self.type=type

class ObjType(Enum):
    OBJ_STRING=0
    OBJ_FUNCTION=1
    OBJ_NATIVE=2

#unlike book this is a indicator class only
class Obj:
    def __init__(self):
        self.type=None
        
class ObjString:
    def __init__(self):
        self.obj=None
        self.length=0
        self.chars=None
        self.hash=0
        
    def __eq__(self, other) -> bool:
        return self.hash==other.hash
    
class ObjFunction:
    def __init__(self) -> None:
        self.obj=None
        self.arity=0
        self.chunk=None
        self.name=None
        
class ObjNative:
    def __init__(self) -> None:
        self.obj=None
        self.function=None
        
def newFunction():
    import chunk
    function=ObjFunction()
    function.arity=0
    function.name=None
    function.obj=allocateObj(ObjType.OBJ_FUNCTION)
    function.chunk=chunk.initChunk()
    return function    

def newNative(function):
    native=ObjNative()
    native.obj=allocateObj(ObjType.OBJ_NATIVE)
    native.function=function #python function
    return native
    
        
def IS_BOOL(value:Value):
    return value.type==ValueType.VAL_BOOL 

def IS_NUMBER(value:Value):
    return value.type==ValueType.VAL_NUMBER

def IS_NIL(value:Value):
    return value.type==ValueType.VAL_NIL

def IS_OBJ(value:Value):
    return value.type==ValueType.VAL_OBJ




def AS_BOOL(value:Value):
    return value.asval

def AS_NUMBER(value:Value):
    return value.asval

#return object type string
def AS_STRING(value:Value):
    return value.asval

#return c string
def AS_CSTRING(value:Value):
    return value.asval.chars

def AS_FUNCTION(value:Value):
    return value.asval

def AS_NATIVE(value:Value):
    return value.asval.function

'''
directly return object identifier in value
'''
def AS_OBJ(value:Value):
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


'''
return a value contain object
'''
def OBJ_VAL(obj):
    value=Value(ValueType.VAL_OBJ,obj)
    return value 

#directly use vm's objects heap to retrieve,the val in constants only contains the pointer to the heap    
def OBJ_TYPE(val:Value):
    return AS_OBJ(val).obj.type 
     
def IS_STRING(val):
    return isObjType(val,ObjType.OBJ_STRING)

def IS_FUNCTION(value:Value):
    return isObjType(value,ObjType.OBJ_FUNCTION)

def IS_NATIVE(value:Value):
    return isObjType(value,ObjType.OBJ_NATIVE)
    

    
def isObjType(val:Value,type:ObjType):
    return IS_OBJ(val) and OBJ_TYPE(val)==type  

def allocateObj(type):
    obj=Obj()
    obj.type=type
    return obj

def hashString(key:str,length:int):
    hash=2166136251
    for i in range(0,length):
        hash^=ord(key[i])
        hash+=16777619
    return hash 

def allocateString(content:str,length:int,hash:int):
    import PLoxVM
    import table
    vMachine=PLoxVM.vm
    strObj=ObjString()
    strObj.chars=content
    strObj.length=length
    strObj.obj=allocateObj(ObjType.OBJ_STRING)
    strObj.hash=hash
    table.tableSet(vMachine.strings,strObj,NIL_VAL())
    return strObj

def takeString(content:str,length:int):
    import table
    import PLoxVM
    hash=hashString(content,length)
    interned=table.tableFindStrings(PLoxVM.vm.strings,content,length,hash)
    if interned is not None:
        del content
        return interned
    return allocateString(content,length,hash)  

def copyString(content:str,length:int):
    import table
    import PLoxVM
    hash=hashString(content,length)
    interned=table.tableFindStrings(PLoxVM.vm.strings,content,length,hash)
    if interned is not None:
        return interned
    chars=deepcopy(content)
    return allocateString(chars,length,hash)
    
#represent constant pool of binary exe 
class ValueArray:
    __slots__ = ["values", "count","capacity"]
    def __init__(self,values=[],count=0,capacity=0) -> None:
        self.capacity=capacity
        self.count=count 
        self.values=[]
        
def initValueArray():
    return ValueArray()

def growCapacity(oldCapacity):
    if oldCapacity<8:
        return 8
    else:
        return oldCapacity*2

def writeValueArray(array:ValueArray,value:Value):
    if array.capacity<array.count+1:
        oldCapacity=array.capacity
        array.capacity=growCapacity(oldCapacity)
        temp_val=array.values 
        temp_count=array.count 
        array.values=[None]*array.capacity
        array.values[0:temp_count]=temp_val
    array.values[array.count]=value
    array.count+=1
        
    
def freeValueArray(array,value:Value):
    del array  
    return ValueArray([],0,0)

def valuesEqual(a:Value,b:Value)->bool:
    if a.type!=b.type:
        return False 
    t=a.type 
    if t==ValueType.VAL_BOOL:
        return AS_BOOL(a)==AS_BOOL(b)
    elif t==ValueType.VAL_NIL:
        return True
    elif t==ValueType.VAL_NUMBER:
        return AS_NUMBER(a)==AS_NUMBER(b)
    elif t==ValueType.VAL_OBJ:
        aString=AS_CSTRING(a)
        bString=AS_CSTRING(b)
        assert type(aString) is str 
        assert type(bString) is str 
        return a==b 
    else:
        return False

def printValue(value:Value):
    if value.type==ValueType.VAL_NUMBER:
        print("{}".format(AS_NUMBER(value)))
    elif value.type==ValueType.VAL_NIL:
        print("nil")
    elif value.type==ValueType.VAL_BOOL:
        print("TRUE" if AS_BOOL(value) else "FALSE")
    elif value.type==ValueType.VAL_OBJ:
        printObject(value)
        
def printObject(value:Value):
    t=OBJ_TYPE(value)
    if t==ObjType.OBJ_STRING:
        print(AS_CSTRING(value))
    elif t==ObjType.OBJ_FUNCTION:
        printFunction(AS_FUNCTION(value))
    elif t==ObjType.OBJ_NATIVE:
        print("<native fn>")
    else:
        pass
        
        
def printFunction(function:ObjFunction):
    if function.name is None:
        print("<script>")
        return
    print("<fn {}>".format(function.name.chars))
    
    
    


        
    
        
        
