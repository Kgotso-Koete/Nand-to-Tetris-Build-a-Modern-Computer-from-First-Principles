from Token import *
from Character import *  
class VMwriter:

    def __init__(self):
        """ Creates a new file and prepares it for writing VM commands"""
        self.cmd_path = None 
        self.IS_directory = None
        self.input_file_path = None
        self.current_file_read = None
        self.output_file_path = None 
        # key data structures
        self.VM_commands = []
        self.segments = {"var": "local", "argument":"argument","this":"this", "that":"that", "temp":"temp", "static":"static", "constant":"constant", "pointer":"pointer"}
        self.operators = {"+":"add", "-":"sub", "neg":"neg","=":"eq", ">":"gt",
                         "<":"lt", "&":"and", "|":"or", "~":"not"}
        self.counter = 0 
        self.symbol_table = None
        self.num_functions = {"if":-1, "while":-1}      
        return
   

    def writePush(self, token=None, segment=None, index=None):  
        """ Writes a VM push command """ 
        if token: 
            # push subroutine table variables
            if token.ascii in self.symbol_table.subroutine_table.keys(): 
                segment = self.segments[ self.symbol_table.subroutine_table[token.ascii]["kind"] ]
                index = self.symbol_table.subroutine_table[token.ascii]["kind_index"]
                self.VM_commands.append("push " + segment + " " + str(index)) 
            # push class table variables  
            elif token.ascii in self.symbol_table.class_table.keys(): 
                segment = self.segments[ self.symbol_table.subroutine_table[token.ascii]["kind"] ]
                index = self.symbol_table.subroutine_table[token.ascii]["kind_index"]
                self.VM_commands.append("push " + segment + " " + str(index)) 
            # push the integer constant
            elif token.type == "integerConstant": self.VM_commands.append("push constant " + token.ascii)
            # push the stringConstant 
            elif token.type == "stringConstant": 
                self.VM_commands.append("push constant " + str(len(token.ascii)))
                self.writeCall(className="String", subroutineName="new", nArgs=1)
                for char in token.ascii:
                    self.VM_commands.append("push constant " + str(ord(char)))
                    self.writeCall(className="String", subroutineName="appendChar", nArgs=2)
            # push keywordConstant
            elif token.ascii in ['true', 'false', 'null']:
                if token.ascii in ['false', 'null']: self.VM_commands.append("push constant " + str(0)) 
                if token.ascii in ['true']: 
                    self.VM_commands.append("push constant " + str(0)) 
                    self.WriteArithmetic("~")              
        else:   
            self.VM_commands.append("push " + segment + " " + str(index)) 
        return   

    def writePop(self, token=None, segment=None, index=None):
        """ Writes a VM pop command """ 
        if token:
            if token.ascii in self.symbol_table.subroutine_table.keys(): 
                segment = self.segments[ self.symbol_table.subroutine_table[token.ascii]["kind"] ]
                index = self.symbol_table.subroutine_table[token.ascii]["kind_index"]
                self.VM_commands.append("pop " + segment + " " + str(index)) 
            elif token.ascii in self.symbol_table.class_table.keys(): 
                segment = self.segments[ self.symbol_table.subroutine_table[token.ascii]["kind"] ]
                index = self.symbol_table.subroutine_table[token.ascii]["kind_index"]
                self.VM_commands.append("pop " + segment + " " + str(index)) 
        else:
            self.VM_commands.append("pop " + segment + " " + str(index)) 
        # self.print_VM_code()  
        return
    
    def WriteArithmetic(self, operator=None,term_count=None):
        """ Writes a VM arithmetic command  """ 
        if operator in self.operators: self.VM_commands.append(self.operators[operator])
        elif operator == "*": self.VM_commands.append("call Math.multiply " + str(term_count)) 
        elif operator == "/": self.VM_commands.append("call Math.divide " + str(term_count))
        return  
    
    def WriteLabel(self, label=None, function=None, count=None):
        """ Writes a VM label command """ 
        if count:self.VM_commands.append("label " + label + str(self.num_functions[function] - count)) 
        else: self.VM_commands.append("label " + label + str(self.num_functions[function])) 
        return
    
    def WriteGoto(self, label=None, function=None, count=None):
        """ Writes a VM go-to command """ 
        if count:self.VM_commands.append("goto "+ label + str(self.num_functions[function] - count)) 
        else: self.VM_commands.append("goto "+ label + str(self.num_functions[function])) 
        return
    
    def WriteIf(self, label=None, function=None, count=None):   
        """ Writes a VM If-goto command """   
        if count:pass 
        else: self.VM_commands.append("if-goto "+ label + str(self.num_functions[function])) 
        return
    
    def writeCall(self, className=None, subroutineName=None, nArgs=None):
        """ Writes a VM call command """ 
        if className: self.VM_commands.append("call " + className + "." + subroutineName + " " + str(nArgs))
        else: self.VM_commands.append("call " + subroutineName + " " + str(nArgs))
   
        return
    
    def writeFunction(self, Class, Subroutine, nLocals):
        """ Writes a VM function command """  
        self.VM_commands.append("function " + Class + "." + Subroutine + " " + str(nLocals))
        return

    def writeReturn(self, subroutine_type): 
        """ Writes a VM return command """
        if subroutine_type == "void":         
            self.VM_commands.append("push constant 0")
            self.VM_commands.append("return") 
        else: 
            self.VM_commands.append("return") 
        return
    
    def print_VM_code(self): 
        for item in self.VM_commands: print(item)
    
    def write_VM_code(self):
        with open(self.output_file_path, 'w') as log: 
            for i in range(len(self.VM_commands)): 
                log.write('{}\n'.format(self.VM_commands[i]))
        return
    
    