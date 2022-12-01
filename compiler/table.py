TABLE_MAX_LOAD=0.75
import value

class Entry:
    def __init__(self) -> None:
        self.key=None
        self.value=None

class Table:
    def __init__(self) -> None:
        self.count=None
        self.capacity=None
        self.entries=list()
        
def initTable(table:Table):
    table.count=0
    table.capacity=0
    table.entries=list()
    
def freeTable(table:Table):
    table.entries.clear()
    initTable(table)
    
def markTable(table:Table):
    import memory
    for i in range(table.capacity):
        entry=table.entries[i]
        memory.markObject(entry.key)
        memory.markValue(entry.value)
        
def tableRemoveWhite(table:Table):
    for i in range(table.capacity):
        e=table.entries[i]
        if e.key is not None and not e.key.obj.isMarked:
            tableDelete(table,e.key)
    
    
def tableGet(table:Table,key):
    if table.count==0:
        return False,None
    entry_idx=findEntry(table,table.entries,table.capacity,key)
    if table.entries[entry_idx].key is None:
        return False,None
    return True,table.entries[entry_idx]
    
def tableSet(table:Table,key,val:value.Value)->bool:
    if table.count+1>table.capacity*TABLE_MAX_LOAD:
        capacity=value.growCapacity(table.capacity)
        adjustCapacity(table,capacity)
    entry_idx=findEntry(table,table.entries,table.capacity,key)
    isNewKey = table.entries[entry_idx].key is None
    if isNewKey and value.IS_NIL(table.entries[entry_idx].value):
        table.count+=1 
    table.entries[entry_idx].key=key
    table.entries[entry_idx].value=val
    return isNewKey

def tableDelete(table:Table,key:value.ObjString):
    if table.count==0:
        return False
    entry_idx=findEntry(table,table.entries,table.capacity,key)
    if table.entries[entry_idx].key is None:
        return False
    #put a tombstone
    table.entries[entry_idx].key=None
    table.entries[entry_idx].value=value.BOOL_VAL(True)
    return True

def tableFindStrings(table:Table,content,length,hash):
    if table.count==0:
        return None 
    index=hash%table.capacity
    while True:
        entry=table.entries[index]
        if entry.key is None:
            if value.IS_NIL(entry.value):
                return None
        elif entry.key.length==length and entry.key.hash==hash and content==entry.key.chars:
            return entry.key
        index= (index+1)%table.capacity  
    
def tableAddAll(f:Table,t:Table):
    for i in range(0,f.capacity):
        entry=f.entries[i]
        if entry.key is not None:
            tableSet(t,entry.key,entry.value)
            
def adjustCapacity(table:Table,capacity):
    new_entries=[None]*capacity
    for i in range(0,capacity):
        e=Entry()
        e.key=None
        e.value=value.NIL_VAL()
        new_entries[i]=e
    table.count=0
    for i in range(0,table.capacity):
        e=table.entries[i]
        if e.key is None:
            continue
        dest_idx=findEntry(table,new_entries,capacity,e.key)
        new_entries[dest_idx].key=e.key
        new_entries[dest_idx].value=e.value
        table.count+=1
    table.entries.clear()
    table.entries=new_entries     
    table.capacity=capacity
    
    
def findEntry(table:Table,entries,capacity:int,key:value.ObjString)->int:
    index=key.hash%capacity
    tombstone=None
    while True:
        entry=entries[index]
        if entry.key is None:
            if value.IS_NIL(entry.value): # a true empty slot
                if tombstone is not None:
                    return tombstone
                else:
                    return index
            else:
                if tombstone is None: #record tombstone index
                    tombstone=index  
        elif entry.key==key:
            return index
        index=(index+1)%capacity
    
        
        
    
        
    
    

    

    