from PLoxScanner import Scanner


class PLox(object):
    def __init__(self):
        super().__init__()
        self.data=None
        hadError=False
        
    def runFile(self,filepath:str):
        with open(filepath, 'r') as file:
            self.data = file.read()
        self.run(self.data)
        if PLox.hadError:
            exit(65)
    
    def runPrompt(self):
        while True:
            print(">", end='')
            line=input()
            #print(len(line))
            if(len(line)==0):
                print("Leaving REPL Mode...")
                break
            self.run(line)
            PLox.hadError=False
    
    def run(self,source:str):
        scanner=Scanner(source)
        tokens=scanner.scanTokens()
        for token in tokens:
            print(token)

    @staticmethod
    def error(line:int,message:str):
        PLox.report(line,"",message)

    @staticmethod
    def report(line:int,where:str,message:str):
        print("line {} error, {}:{}".format(line,where,message))
        hadError=True
