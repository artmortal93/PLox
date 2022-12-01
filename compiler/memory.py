
DEBUG_LOG_GC=True
import sys
from value import *
GC_HEAP_GROW_FACTOR=2

def collectGarbage():
    if DEBUG_LOG_GC:
        print("--gc begin")
    markRoots()    
    traceRefereneces()
    import table
    import PLoxVM
    table.tableRemoveWhite(PLoxVM.vm.strings)
    sweep()
    if DEBUG_LOG_GC:
        print("--gc end")
        
def freeObject(obj):
    del obj
    if DEBUG_LOG_GC:
        print("{} free type {}".format(type(object),sys.getsizeof(obj)))
        
def markRoots():
    import PLoxVM
    import table
    for i in range(PLoxVM.vm.stackTop):
        slot=PLoxVM.vm[i]
        markValue(slot)
    for i in range(PLoxVM.vm.frameCount):
        markObject(vm.frames[i].closure)
    upvalue=PLoxVM.vm.openUpvalues
    while upvalue!=None:
        markObject(upvalue)
        upvalue=upvalue.next
    table.markTable(PLoxVM.vm.globals)
        
def markValue(val):
    import value
    if not value.IS_OBJ(val):
        return
    markObject(value.AS_OBJ(val))
    
def growCapacity(oldCapacity):
    if oldCapacity<8:
        return 8
    else:
        return oldCapacity*2
    
def markObject(object):
    if object.obj.isMarked:
        return 
    import value
    import PLoxVM
    if object is None:
        return 
    object.obj.isMarked=True
    if PLoxVM.vm.grayCapacity<PLoxVM.vm.grayCount+1:
        PLoxVM.vm.grayCapacity=growCapacity(PLoxVM.vm.grayCapacity)
        PLoxVM.vm.grayStack=[None]*PLoxVM.vm.grayCapacity
    PLoxVM.vm.grayStack[PLoxVM.vm.grayCount]=object
    PLoxVM.vm.grayCount+=1
    if DEBUG_LOG_GC:
        print("mark a object ",end='')
        value.printValue(value.OBJ_VAL(object))
        
def traceRefereneces():
    import PLoxVM
    while PLoxVM.vm.grayCount>0:
        PLoxVM.vm.grayCount-=1
        object=PLoxVM.vm.grayStack[PLoxVM.vm.grayCount]
        blackenObject(object)
        

def blackenObject(object):
    import table
    t=object.obj.type
    if t==ObjType.OBJ_NATIVE:
        pass
    elif t==ObjType.OBJ_STRING:
        pass 
    elif t==ObjType.OBJ_UPVALUE:
        markValue(object.location) #closed
    elif t==ObjType.OBJ_FUNCTION:
        markObject(object.name)
        markArray(object.chunk.constants)
    elif t==ObjType.OBJ_CLOSURE:
        markObject(object.function)
        for i in range(object.upvalueCount):
            markObject(object.upvalues[i])
    elif t==ObjType.OBJ_CLASS:
        markObject(object.name)
        table.markTable(object.methods)
    elif t==ObjType.OBJ_INSTANCE:
        markObject(object.klass)
        markObject(object.fields)
    elif t==ObjType.OBJ_BOUND_METHOD:
        markValue(object.reciever)
        markObject(object.method)
        
def markArray(array):
    for i in range(array.count):
        markValue(array.values[i])
        
def sweep():
    import PLoxVM
    previous=None
    object=PLoxVM.vm.objects #we implement object chain as a deque
    for o in object:
        if o.isMarked:
            o.isMarked=False
        else:
            object.remove(o)
            del o
        
        
    
        
    
        

    

    