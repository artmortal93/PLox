from chunk import *


def disassembleChunk(chunk:Chunk,name:str):
    print("== {} ==".format(name))
    offset=0
    while offset<chunk.count:
        offset=disassembleInstruction(chunk,offset)

def disassembleInstruction(chunk:Chunk,offset:int):
    print("{:04d}".format(offset),end=' ')
    if offset>0 and chunk.lines[offset]==chunk.lines[offset-1]:
        print("   | ",end='')
    else:
        print("{:04d} ".format(chunk.lines[offset]),end='')
    instruction=chunk.code[offset]
    if instruction is OpCode.OP_RETURN:
        return simpleInstruction("OP_RETURN",offset)
    elif instruction is OpCode.OP_CONSTANT:
        return constantInstruction("OP_CONSTANT",chunk,offset)
    elif instruction is OpCode.OP_NEGATE:
        return simpleInstruction("OP_NEGATE",offset)
    elif instruction is OpCode.OP_ADD:
        return simpleInstruction("OP_ADD",offset)
    elif instruction is OpCode.OP_MULTIPLY:
        return simpleInstruction("OP_MULTIPLY",offset)
    elif instruction is OpCode.OP_DIVIDE:
        return simpleInstruction("OP_DIVIDE",offset)
    elif instruction is OpCode.OP_SUBTRACT:
        return simpleInstruction("OP_SUBTRACE",offset)
    elif instruction is OpCode.OP_NIL:
        return simpleInstruction("OP_NIL",offset)
    elif instruction is OpCode.OP_TRUE:
        return simpleInstruction("OP_TRUE",offset)
    elif instruction is OpCode.OP_FALSE:
        return simpleInstruction("OP_FALSE",offset)
    elif instruction is OpCode.OP_NOT:
        return simpleInstruction("OP_NOT",offset)
    else:
        print("Unknown Op code {}".format(instruction))
        return offset+1
    
def simpleInstruction(name,offset):
    print("{}".format(name))
    return offset+1

def constantInstruction(name:str,chunk:Chunk,offset:int):
    constant=chunk.code[offset+1]
    print("{} {:04d}".format(name,constant),end=' ')
    printValue(chunk.constants.values[constant])
    print("",end='\n')
    return offset+2
    
