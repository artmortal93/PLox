

exprTypes=[
     "Binary : Expr left, Token operator, Expr right",
     "Grouping : Expr expression",
     "Literal : object value",
     "Unary : Token operator, Expr right"
    ]

def defineAst(type:str,baseName:str="Expr")->str:
    memberText='self.{}={}'
    constructorText='def __init__(self'
    indentText='    '
    superText='super().__init__()'
    classText="class {}(Expr): \n"
    className=type.split(':')[0].strip()
    fields=type.split(':')[1].strip()
    fieldTuples=fields.split(',')
    bluePrintText=classText.format(className)
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
    return bluePrintText





