from PLoxDef import *
import PLox


#generate Tree of expression(AST)
class Parser:
    def __init__(self, tokens):
        self.tokens=tokens
        self.current=0 #the one are waiting to check token but not check yet

    def isAtEnd(self)->bool:
        return self.peek().type is TokenType.EOF

    def peek(self)->Token:
        return self.tokens[self.current]

    def previous(self)->Token:
        return self.tokens[self.current-1]

    def advance(self)->Token:
        if not self.isAtEnd():
            self.current+=1
        return self.previous()

    def check(self,type:TokenType)->bool:
        if self.isAtEnd():
            return False
        return self.peek().type==type

    #match any type in types, then advance
    def match(self, *types)->bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True #? then why *args
        return False

    def consume(self,type:TokenType, message:str):
        if self.check(type):
            return self.advance()
        next=self.peek()
        raise self.error(next,message)

    def error(self,token,message):
        PLox.PLox.tokenError(token,message)
        return ParseError()

    #decsent parser starts
    def expression(self)->Expr:
        return self.assignment()

    #mind that assign is left token right expression
    def assignment(self)->Expr:
        expr=self.Or() #may match variable or upstairs
        if self.match(TokenType.EQUAL):
            equals=self.previous()
            value=self.assignment()
            if type(expr) is Variable:
                name=expr.name #get a token
                return Assign(name,value)#that also mean assign should return a val in visitor
            elif isinstance(expr,Get):
                return Set(expr.obj,expr.name,value)
            else:
                self.error(equals,"Invalid assignment target.")
        return expr

    #conflict with python keywords
    def Or(self)->Expr:
        expr=self.And()
        while self.match(TokenType.OR):
            operator=self.previous()
            right=self.And()
            expr=Logical(expr,operator,right)
        return expr

    #conflict with python keywords
    def And(self)->Expr:
        expr=self.equality()
        while self.match(TokenType.AND):
            operator=self.previous()
            right=self.equality()
            expr=Logical(expr,operator,right)
        return expr


    def equality(self)->Expr:
        #note that * are tranlated into while loop
        expr=self.comparison()
        while self.match(TokenType.BANG_EQUAL,TokenType.EQUAL_EQUAL):
            operator=self.previous()
            right=self.comparison()
            expr=Binary(expr,operator,right)
        return expr

    def comparison(self)->Expr:
        expr=self.term()
        while self.match(TokenType.GREATER,TokenType.GREATER_EQUAL,TokenType.LESS,TokenType.LESS_EQUAL):
            operator=self.previous()
            right=self.term()
            expr=Binary(expr,operator,right)
        return expr

    def term(self)->Expr:
        expr=self.factor()
        while self.match(TokenType.MINUS,TokenType.PLUS):
            operator=self.previous()
            right=self.factor()
            expr=Binary(expr,operator,right)
        return expr

    def factor(self)->Expr:
        expr=self.unary()
        while self.match(TokenType.SLASH,TokenType.STAR):
            operator=self.previous()
            right=self.unary()
            expr=Binary(expr,operator,right)
        return expr 

    def unary(self)->Expr:
        if self.match(TokenType.BANG,TokenType.MINUS):
            operator=self.previous()
            right=self.unary()
            return Unary(operator,right)
        else:
            return self.call()

    #the while chain handle the mehod call very well
    #what we left is how we evaluate class.method member
    def call(self)->Expr:
        expr=self.primary()
        while True:
            #can chain multiple chain call object for recursion
            if self.match(TokenType.LEFT_PAREN):
                expr=self.finishCall(expr) #incase multiple chain calls
            elif self.match(TokenType.DOT):
                name=self.consume(TokenType.IDENTIFER,"Expect property name after .")
                expr=Get(expr,name)
            else:
                break
        return expr

    def finishCall(self,callee:Expr)->Expr:
        arguments=[]
        #add argument expression
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments)>=255:
                    self.error(self.peek(),"Too much arguments.")
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
        paren=self.consume(TokenType.RIGHT_PAREN,"Expect ')' after arguments")
        return Call(callee,paren,arguments)

    

    def primary(self)->Expr:
        if self.match(TokenType.FALSE):
            return Literal(False)
        elif self.match(TokenType.TRUE):
            return Literal(True)
        elif self.match(TokenType.NIL):
            return Literal(None)
        elif self.match(TokenType.NUMBER,TokenType.STRING):
            return Literal(self.previous().literal)
        elif self.match(TokenType.SUPER):
            keyword=self.previous()
            self.consume(TokenType.DOT,"Expect dot after super")
            method=self.consume(TokenType.IDENTIFER,"Expect superclass method name")
            return Super(keyword,method)
        elif self.match(TokenType.THIS):
            return This(self.previous())
        elif self.match(TokenType.IDENTIFER):
            return Variable(self.previous())
        elif self.match(TokenType.LEFT_PAREN):
            expr=self.expression() #in this case. a expression has been consume and advanced
            self.consume(TokenType.RIGHT_PAREN,'Expect ) after expression.')
            return Grouping(expr)
        
        #the error of other not processed yet token (or/if/while/for)
        raise self.error(self.peek(),"Expect expression.")

    #reset to another possible statment if error was met, but the error should not be
    #critical
    def synchornize(self):
        self.advance() #omit the wrong token
        while not self.isAtEnd():
            if self.previous().type==TokenType.SEMICOLON:
                return
            typeToStart=[TokenType.CLASS,TokenType.FUN,TokenType.VAR,TokenType.FOR,TokenType.IF,TokenType.WHILE,TokenType.PRINT,TokenType.RETURN]
            if self.peek().type in typeToStart:
                #self.advance()
                return
            self.advance()

    def parse(self):
        statments=[] #array of stmt
        while not self.isAtEnd():
            statments.append(self.declaration())#error handling in declaration method
        return statments

    #statment syntax descent parsing part
    def statment(self)->Stmt:
        if self.match(TokenType.PRINT):
            return self.printStatment()
        if self.match(TokenType.RETURN):
            return self.returnStatment()
        if self.match(TokenType.WHILE):
            return self.whileStatment()
        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        if self.match(TokenType.FOR):
            return self.forStatment()
        if self.match(TokenType.IF):
            return self.ifStatment()
        return self.expressionStatment()

    def declaration(self)->Stmt:
        try:
            if self.match(TokenType.FUN):
                return self.function("function")
            elif self.match(TokenType.CLASS):
                return self.classDeclaration()
            elif self.match(TokenType.VAR):
                return self.varDeclaration()
            else:
                return self.statment()
        except ParseError as e:
            self.synchornize()

    def printStatment(self)->Stmt:
        value=self.expression()
        self.consume(TokenType.SEMICOLON,"Expect ';' after value")
        return Print(value)
        

    def expressionStatment(self)->Stmt:
        expr=self.expression()
        self.consume(TokenType.SEMICOLON,"Expect ';' after value")
        return Expression(expr)

    def varDeclaration(self)->Stmt:
        name=self.consume(TokenType.IDENTIFER,"Expect variable name")
        initializer=None
        if self.match(TokenType.EQUAL):
            initializer=self.expression() #could be bool/number/string...
        self.consume(TokenType.SEMICOLON,"Expect ';' after variable declatation")
        return Var(name,initializer)

    def block(self)->list:
        statments=[]
        while not self.isAtEnd() and not self.check(TokenType.RIGHT_BRACE):
            statments.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE,"Expect '}' after block.")
        return statments

    def ifStatment(self)->Stmt:
        self.consume(TokenType.LEFT_PAREN,"Expect '(' after 'if'.")
        condition=self.expression()
        self.consume(TokenType.RIGHT_PAREN,"Expect ')' after if condition")
        thenBranch=self.statment()
        elseBranch=None
        if self.match(TokenType.ELSE):
            elseBranch=self.statment()
        return If(condition,thenBranch,elseBranch)

    def whileStatment(self)->Stmt:
        self.consume(TokenType.LEFT_PAREN,"Expect '(' after 'while'.")
        condition=self.expression()
        self.consume(TokenType.RIGHT_PAREN,"Expect ')' after while condition")
        body=self.statment()
        return While(condition,body)

    def forStatment(self)->Stmt:
        self.consume(TokenType.LEFT_PAREN,"Expect '(' after 'for'.")
        initializer=None
        condition=None
        increment=None
        if self.match(TokenType.SEMICOLON): #first var is omited
            initializer=None
        elif self.match(TokenType.VAR):
            initializer=self.varDeclaration()#must be a var decal
        else:
            initializer=self.expressionStatment()#or a statment,variable could be declare outside
        if not self.check(TokenType.SEMICOLON):
            condition=self.expression()
        self.consume(TokenType.SEMICOLON,"Expect ; after loop condition")
        #second clause come with one or no expression and semicolon
        if not self.check(TokenType.RIGHT_PAREN):
            increment=self.expression()
        self.consume(TokenType.RIGHT_PAREN,"Expect ) after for clauses")
        #third clause come with one or no expression and a right brace
        body=self.statment()
        if increment is not None :
            body=Block([body,Expression(increment)])#execute,+1 then go away
        if condition is None:
            condition=Literal(True)
        body=While(condition,body)
        if initializer is not None:
            body=Block([initializer,body])
        return body 

    #parse function declaration stmt
    def function(self,kind:str)->Stmt:
        name=self.consume(TokenType.IDENTIFER,"Expect {} name".format(kind))
        self.consume(TokenType.LEFT_PAREN,"Expect '(' after {} name".format(kind))
        parameters=[]
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters)>=255:
                    self.error(self.peek(),"Can not have too many params")
                parameters.append(self.consume(TokenType.IDENTIFER,"Expect patameter name"))
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN,"Expect ')' after params.")
        self.consume(TokenType.LEFT_BRACE,"Expect fun blocks")
        body=self.block()
        return Function(name,parameters,body)

    def returnStatment(self)->Stmt:
        keyword=self.previous()
        value=None
        if not self.check(TokenType.SEMICOLON):
            value=self.expression()
        self.consume(TokenType.SEMICOLON,"Expect ';' after rtn value")
        return Return(keyword,value)

    def classDeclaration(self)->Stmt:
        name=self.consume(TokenType.IDENTIFER,"Expect Class Name")
        superclass=None
        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFER,"Expect Super name")
            superclass=Variable(self.previous())
        self.consume(TokenType.LEFT_BRACE,"Expect { before class body")
        methods=[]
        while not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd():
            methods.append(self.function("method"))
        self.consume(TokenType.RIGHT_BRACE,"Expect } after class body")
        return Class(name,superclass,methods)

























