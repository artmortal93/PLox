
DEBUG_LOG_GC=True
import sys

def collectGarbage():
    if DEBUG_LOG_GC:
        print("--gc begin")
    markRoots()    
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
    table.markTable(PLoxVM.vm.globals)
        
def markValue(val):
    import value
    if not value.IS_OBJ(val):
        return
    markObject(value.AS_OBJ(val))
    
def markObject(object):
    import value
    if object is None:
        return 
    object.obj.isMarked=True
    if DEBUG_LOG_GC:
        print("mark a object ",end='')
        value.printValue(value.OBJ_VAL(object))
    

    