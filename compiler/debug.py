import chunk
import value

def disassembleChunk(c:chunk.Chunk,name:str):
    print("== {} ==".format(name))
    offset=0
    while offset<c.count:
        offset=disassembleInstruction(c,offset)

def disassembleInstruction(c:chunk.Chunk,offset:int):
    print("{:04d}".format(offset),end=' ')
    if offset>0 and c.lines[offset]==c.lines[offset-1]:
        print("   | ",end='')
    else:
        print("{:04d} ".format(c.lines[offset]),end='')
    instruction=c.code[offset]
    if instruction is chunk.OpCode.OP_RETURN:
        return simpleInstruction("OP_RETURN",offset)
    elif instruction is chunk.OpCode.OP_CONSTANT:
        return constantInstruction("OP_CONSTANT",c,offset)
    elif instruction is chunk.OpCode.OP_NEGATE:
        return simpleInstruction("OP_NEGATE",offset)
    elif instruction is chunk.OpCode.OP_ADD:
        return simpleInstruction("OP_ADD",offset)
    elif instruction is chunk.OpCode.OP_MULTIPLY:
        return simpleInstruction("OP_MULTIPLY",offset)
    elif instruction is chunk.OpCode.OP_DIVIDE:
        return simpleInstruction("OP_DIVIDE",offset)
    elif instruction is chunk.OpCode.OP_SUBTRACT:
        return simpleInstruction("OP_SUBTRACE",offset)
    elif instruction is chunk.OpCode.OP_NIL:
        return simpleInstruction("OP_NIL",offset)
    elif instruction is chunk.OpCode.OP_TRUE:
        return simpleInstruction("OP_TRUE",offset)
    elif instruction is chunk.OpCode.OP_FALSE:
        return simpleInstruction("OP_FALSE",offset)
    elif instruction is chunk.OpCode.OP_NOT:
        return simpleInstruction("OP_NOT",offset)
    elif instruction is chunk.OpCode.OP_EQUAL:
        return simpleInstruction("OP_EQUAL",offset)
    elif instruction is chunk.OpCode.OP_GREATER:
        return simpleInstruction("OP_GREATER",offset)
    elif instruction is chunk.OpCode.OP_LESS:
        return simpleInstruction("OP_LESS",offset)
    elif instruction is chunk.OpCode.OP_PRINT:
        return simpleInstruction("OP_PRINT",offset)
    elif instruction is chunk.OpCode.OP_POP:
        return simpleInstruction("OP_POP",offset)
    elif instruction is chunk.OpCode.OP_DEFINE_GLOBAL:
        return constantInstruction("OP_DEFINE_GLOBAL",c,offset)
    elif instruction is chunk.OpCode.OP_GET_GLOBAL:
        return constantInstruction("OP_GET_GLOBAL",c,offset)
    elif instruction is chunk.OpCode.OP_SET_GLOBAL:
        return constantInstruction("OP_SET_GLOBAL",c,offset)
    elif instruction is chunk.OpCode.OP_GET_LOCAL:
        return byteInstruction("OP_GET_LOCAL",c,offset)
    elif instruction is chunk.OpCode.OP_SET_LOCAL:
        return byteInstruction("OP_SET_LOCAL",c,offset)
    elif instruction is chunk.OpCode.OP_JUMP:
        return jumpInstruction("OP_JUMP",1,c,offset)
    elif instruction is chunk.OpCode.OP_JUMP_IF_FALSE:
        return jumpInstruction("OP_JUMP_IF_FALSE",1,c,offset)
    elif instruction is chunk.OpCode.OP_LOOP:
        return jumpInstruction("OP_LOOP",-1,c,offset)
    elif instruction is chunk.OpCode.OP_CALL:
        return byteInstruction("OP_CALL",c,offset)
    elif instruction is chunk.OpCode.OP_CLOSURE:
        offset+=1
        constant=c.code[offset]
        offset+=1
        print("{} {:04d}".format("OP_CLOSURE",constant),end='')
        value.printValue(c.constants.values[constant])
        print('\n',end='')
        function=value.AS_FUNCTION(c.constants.values[constant])
        for j in range(0,function.upvalueCount):
            isLocal=c.code[offset]
            offset+=1
            index=c.code[offset]
            offset+=1
            locInfo="local" if isLocal else "upvalue"
            print("{:04d}  |  {}  {}".format(offset-2,locInfo,index))
        return offset
    elif instruction is chunk.OpCode.OP_GET_UPVALUE:
        return byteInstruction("OP_GET_UPVALUE",chunk,offset)
    elif instruction is chunk.OpCode.OP_SET_UPVALUE:
        return byteInstruction("OP_SET_UPVALUE",chunk,offset)
    elif instruction is chunk.OpCode.OP_CLOSE_UPVALUE:
        return simpleInstruction("OP_CLOSE_UPVALUE",offset)
    else:
        print("Unknown Op code {}".format(instruction))
        return offset+1
    
def simpleInstruction(name,offset):
    print("{}".format(name))
    return offset+1

def constantInstruction(name:str,c,offset:int):
    constant=c.code[offset+1]
    print("{} {:04d}".format(name,constant),end=' ')
    value.printValue(c.constants.values[constant])
    print("",end='\n')
    return offset+2

def byteInstruction(name,c,offset):
    slot=c.code[offset+1]
    print("{}:{}".format(name,slot))
    return offset+2

def jumpInstruction(name,sign,c,offset):
    jump1=c.code[offset+1]<<8
    jump2=c.code[offset+2]
    jump=jump1 | jump2 
    print("{} {}->{}".format(name,offset,offset+3+sign*jump))
    return offset+3


    
