

exprTypes=[
     "Binary : Expr left, Token operator, Expr right",
     "Grouping : Expr expression",
     "Literal : object value",
     "Unary : Token operator, Expr right"
    ]


def defineAccept(text:str,baseName:str,className:str)->str:
    indentText='    '
    methodText='def accept(self,visitor):\n'
    text+='\n'
    text+=indentText
    text+=methodText
    text+=indentText*2
    text+='return visitor.visit{}{}(self)\n'.format(className,baseName)
    return text


def defineAst(type:str,baseName:str="Expr")->str:
    memberText='self.{}={}'
    constructorText='def __init__(self'
    indentText='    '
    superText='super().__init__()'
    classText="class {}({}): \n"
    className=type.split(':')[0].strip()
    fields=type.split(':')[1].strip()
    fieldTuples=fields.split(',')
    bluePrintText=classText.format(className,baseName)
    bluePrintText+=indentText
    bluePrintText+=constructorText
    for t in fieldTuples:
        t=t.strip()
        tClass=t.split(' ')[0]
        tName=t.split(' ')[1]
        tInit=',{}:{}'.format(tName,tClass)
        bluePrintText+=tInit
    bluePrintText+='):\n'
    for t in fieldTuples:
        t=t.strip()
        tName=t.split(' ')[1]
        bluePrintText+=indentText
        bluePrintText+=indentText
        bluePrintText+=memberText.format(tName,tName)
        bluePrintText+='\n'
    bluePrintText=defineAccept(bluePrintText,baseName,className)
    return bluePrintText


def defineVisitor(baseName:str,types:list):
    indentText='    '
    annontationText='@abstractmethod'
    bluePrintText=''
    bluePrintText+='class Visitor(ABC):\n'
    for type in types:
        typeName=type.split(':')[0].strip()
        bluePrintText+=indentText
        bluePrintText+=annontationText
        bluePrintText+='\n'
        bluePrintText+=indentText
        bluePrintText+='def visit{}{}(self,{}):\n'.format(typeName,baseName,baseName)
        bluePrintText+=indentText*2
        bluePrintText+='pass\n'
        bluePrintText+='\n'
    return bluePrintText







