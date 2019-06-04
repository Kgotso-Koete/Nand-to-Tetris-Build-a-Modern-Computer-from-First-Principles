import xml.etree.ElementTree as ET     
from Scanner import *
from Lexer import *
import sys
import itertools
from SymbolTable import *
from VMwriter import *
 
# With coding help from : http://parsingintro.sourceforge.net/ 
class Parser:
    def __init__(self):
        self.cmd_path = None 
        self.IS_directory = None
        self.input_file_path = None # input file used to parse code
        self.output_file_path = None  # output file where xml will be written
        self.current_file_read = None
        self.lexer = None
        #-------------------------------------------------------------------
        # iterative data structures
        #-------------------------------------------------------------------
        self.token_list = None
        self.ITERABLE_token_list = None
        self.current_token = None
        self.previous_token = None
        self.next_token = None  
        self.token_index = -1
        #-------------------------------------------------------------------
        # XML tree variables
        #-------------------------------------------------------------------
        self.xml_root = None 
        self.tree_list = [] 
        #-------------------------------------------------------------------
        # variables for compiling VM code
        #-------------------------------------------------------------------
        self.symbol_table = None
        self.VMwriter = VMwriter()
    
    def get_token_list(self):  
        # initialise and clean up previous iterations
        self.token_list = None
        self.ITERABLE_token_list = None
        self.current_token = None
        self.previous_token = None
        self.next_token = None  
        self.token_index = -1
        # create and store tokens
        self.lexer = Lexer(self.input_file_path) 
        self.token_list = self.lexer.get_token_types() 
        self.ITERABLE_token_list = iter(self.token_list) 
        self.token_PEEKING_list = self.ITERABLE_token_list
        return
     
    def print_iterated_tokens(self):
        print("| Current token:", self.current_token.ascii,
             " | Current token type:", self.current_token.type, 
              "| Next token val:", self.next_token.ascii, " |")
    def print_all_tokens(self): 
        for t in self.token_list:  
            print("|", "Token val: ", t.ascii, " | ", "Token type: ", t.type, " |")   
        
    def create_xml(self): 
        """ Writes the tokens in XML format """ 
        # compile all statements
        self.parse() 
        # create tree
        self.tree_list.append((self.xml_root, self.output_file_path))  
        return 
    
    def write_xml(self):   
        
        from xml.dom import minidom

        for root in self.tree_list: 
            pretty_tree = self.prettify(root[0])
            pretty_tree = pretty_tree[22:].lstrip()
            # print(pretty_tree)  
            with open(root[1], "w") as f: f.write(pretty_tree)

        self.VMwriter.print_VM_code() 
        self.VMwriter.write_VM_code()
        return 
    
    def prettify(self,elem):
        """Return a pretty-printed XML string for the Element """
        # with great help from: https://stackoverflow.com/a/17402424
        from xml.dom import minidom
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")

    def add_xml_element(self, parent_node):  
        ET.SubElement(parent_node, self.current_token.type).text = ' ' + self.current_token.ascii + ' '
        return
                               
    #-------------------------------------------------------------------
    # fetching, checking and adding xml tokens            
    #-------------------------------------------------------------------
    def get_token(self):
        self.previous_token = self.current_token 
        self.current_token = next(self.ITERABLE_token_list)
        self.token_index += 1 
        self.peek_next_token()  
        # self.print_iterated_tokens()       
        return self.current_token  
    
    def peek_next_token(self): 
        if self.token_index < len(self.token_list)-1:    
            self.next_token = next(self.token_PEEKING_list)
            self.ITERABLE_token_list = (value for g in ([self.next_token], self.ITERABLE_token_list) for value in g)
        return self.next_token
 
    def consume(self, tkn_val=[], tkn_type=None, parent_node=None, ast_parent=None):
        """ Consume a token of a given type and get the next token """
        if len(tkn_val) > 0:
            if self.current_token.ascii in tkn_val and self.current_token.type == tkn_type: 
                self.add_xml_element(parent_node)
                self.get_token()  
        else:
            if self.current_token.type == tkn_type : 
                self.add_xml_element(parent_node) 
                self.get_token() 
        return 

    #-------------------------------------------------------------------
    # key driver: parse
    #-------------------------------------------------------------------
    def parse(self):      
        self.get_token()
        # initialise key data structures
        self.symbol_table = SymbolTable()
        self.VMwriter.symbol_table = self.symbol_table
        # begin compiling
        self.compile_class()
        return 
    
    #--------------------------------------------------------
    # recursive descent: class
    #--------------------------------------------------------
    def compile_class(self):   
        """ 'class' className '{' classVarDec* subroutineDec* '}' """

        # intialise the tree
        Class_node = ET.Element("class")   
        self.xml_root = Class_node  
        #--------------------------------------------------------
        # component: 'class' 
        self.consume(tkn_val=["class"], tkn_type="keyword", parent_node=Class_node)   
        # component: className
        self.symbol_table.new_class_scope(self.current_token.ascii) 
        self.compile_className(parent_node= Class_node)   
        # component: '{'
        self.consume(tkn_val=["{"], tkn_type="symbol", parent_node=Class_node) 
        # component: classVarDec* subroutineDec*  
        while not (self.next_token.type == "EOF"): 
            # component: classVarDec*
            self.compile_classVarDec(parent_node=Class_node)
            # component: subroutineDec*
            self.compile_subroutineDec(parent_node= Class_node)
        # component: '}' 
        self.consume(tkn_val=["}"], tkn_type="symbol", parent_node=Class_node)  
        # component: EOF 
        #-------------------------------------------------------- 
        return 

    #--------------------------------------------------------
    # recursive descent: className
    #--------------------------------------------------------
    def compile_className(self, parent_node):   
        """identifier"""  
        self.consume(tkn_val=[], tkn_type="identifier", parent_node=parent_node) # component: 'class' 
        return 

    #--------------------------------------------------------
    # recursive descent: classVarDec
    #--------------------------------------------------------
    def compile_classVarDec(self, parent_node): 
        """ ('static' | 'field' ) type varName (',' varName)* ';' """
        
        while self.current_token.ascii in ['static', 'field']:
            # new XML parent 
            classVarDec_node = ET.SubElement(parent_node, "classVarDec") 
            #--------------------------------------------------------
            # component: ('static' | 'field' ) 
            self.symbol_table.update_class_table(self.token_index, self.current_token.ascii, self.previous_token.ascii, self.next_token.ascii)
            self.consume(tkn_val=[], tkn_type="keyword", parent_node=classVarDec_node)  
            # component: type 
            self.symbol_table.update_class_table(self.token_index, self.current_token.ascii, self.previous_token.ascii, self.next_token.ascii)
            self.compile_type(parent_node=classVarDec_node) 
            
            while ";" not in self.current_token.ascii:  
                # component: varName   
                self.symbol_table.update_class_table(self.token_index, self.current_token.ascii, self.previous_token.ascii, self.next_token.ascii)
                self.compile_varName(parent_node=classVarDec_node) 
                # component: ,
                self.consume(tkn_val=[","], tkn_type="symbol", parent_node=classVarDec_node)
            self.consume(tkn_val=[";"], tkn_type="symbol", parent_node=classVarDec_node)
        #--------------------------------------------------------
        return

    #--------------------------------------------------------
    # recursive descent: type
    #--------------------------------------------------------
    def compile_type(self, parent_node): 
        """ 'int' | 'char' | 'boolean' | className """
        # component:'int' | 'char' | 'boolean' 
        if self.current_token.ascii in ['int', 'char', 'boolean']:
            self.consume(tkn_val=['int', 'char', 'boolean'], tkn_type="keyword", parent_node=parent_node)
        # component: | className 
        else: 
            self.compile_className(parent_node=parent_node) 
        return
    
    #--------------------------------------------------------
    # recursive descent: varName
    #--------------------------------------------------------
    def compile_varName(self, parent_node):   
        """identifier"""  
        self.consume(tkn_val=[], tkn_type="identifier", parent_node=parent_node)
        return
    
    #--------------------------------------------------------
    # recursive descent: subroutineName
    #--------------------------------------------------------
    def compile_subroutineName(self, parent_node):   
        """identifier"""  
        self.consume(tkn_val=[], tkn_type="identifier", parent_node=parent_node)
        return 

    #--------------------------------------------------------
    # recursive descent: subroutineDec
    #--------------------------------------------------------   
    def compile_subroutineDec(self, parent_node): 
        """  
        ('constructor' | 'function' | 'method') ('void' | type) 
        subroutineName'(' parameterList ')' subroutineBody 
        """
        #--------------------------------------------------------
        f = open("permanent_variables.txt","w+")
        f.write(self.current_token.ascii) # write permanent variable
        f = open("permanent_variables.txt","r")  
        subroutine_kind = f.read() # save permanent variable
        f = open("permanent_variables.txt","w+") 
        f.seek(0)
        f.truncate()
        f.close() # delete file contents and close file
        #--------------------------------------------------------
        # new XML parent 
        subroutineDec_node = ET.SubElement(parent_node, "subroutineDec")  
        #--------------------------------------------------------
        # component: ('constructor' | 'function' | 'method')
        self.consume(tkn_val=['constructor', 'function', 'method'], tkn_type="keyword", parent_node=subroutineDec_node) 
        self.VMwriter.num_functions["if"] = -1  
        self.VMwriter.num_functions["while"] = -1   
        # component: ('void' | type)  
        if self.current_token.ascii == "void":
            self.consume(tkn_val=["void"], tkn_type="keyword", parent_node=subroutineDec_node) 
        else: 
            self.compile_type(parent_node=subroutineDec_node) 
         
        # component: subroutineName   
        self.symbol_table.new_subroutine_scope(subroutine_kind, self.previous_token.ascii , self.current_token.ascii)   
        self.compile_subroutineName(parent_node=subroutineDec_node) 
 
        # check if list is empty (print space with closing tag if empty)
        if self.current_token.ascii == "(" and self.next_token.ascii == ")": 
            # component: '(' 
            self.consume(tkn_val=["("], tkn_type="symbol", parent_node=subroutineDec_node)
            # component: parameterList 
            self.compile_parameterList(empty=True, parent_node=subroutineDec_node)  
            # component: ')'  
            self.consume(tkn_val=[")"], tkn_type="symbol", parent_node=subroutineDec_node)
        else:
            # component: '('
            self.consume(tkn_val=["("], tkn_type="symbol", parent_node=subroutineDec_node)
            # component: parameterList 
            self.symbol_table.compiling_state = "args" 
            self.compile_parameterList(empty=False, parent_node=subroutineDec_node)  
            # component: ')'  
            self.consume(tkn_val=[")"], tkn_type="symbol", parent_node=subroutineDec_node)
        # component: subroutineBody 
        self.compile_subroutineBody(parent_node=subroutineDec_node)    
        #--------------------------------------------------------
        return   
    
    #--------------------------------------------------------
    # recursive descent: parameterList 
    #-------------------------------------------------------- 
    def compile_parameterList(self, empty, parent_node):  
        """ : ( (type varName) (',' type varName)*)? """ 
         
        # new XML parent   
        if empty:parameterList_node = ET.SubElement(parent_node, "parameterList").text = " " + "\n"
        if not empty:parameterList_node = ET.SubElement(parent_node, "parameterList")
        #--------------------------------------------------------     
        while not (self.current_token.ascii == ")" ): 
            # component: type    
            self.compile_type(parent_node=parameterList_node) 
            # component: varName
            self.symbol_table.update_subroutine_table(self.token_index, self.current_token.ascii, self.previous_token.ascii, self.next_token.ascii)
            self.compile_varName(parent_node=parameterList_node)  
            # component: , 
            self.consume(tkn_val=[","], tkn_type="symbol", parent_node=parameterList_node)
        #--------------------------------------------------------
        return 
    
    #--------------------------------------------------------
    # recursive descent: subroutineBody
    #--------------------------------------------------------
    def compile_subroutineBody(self, parent_node):  
        """ '{' varDec* statements '}' """ 

        # new XML parent 
        subroutineBody_node = ET.SubElement(parent_node, "subroutineBody") 
        #-------------------------------------------------------- 
        # component: '{'  
        self.consume(tkn_val=["{"], tkn_type="symbol", parent_node=subroutineBody_node)
        # component: varDec* 
        self.compile_varDec(parent_node=subroutineBody_node)  
        self.VMwriter.writeFunction(self.symbol_table.class_name, self.symbol_table.subroutine_name, self.symbol_table.var_count["var"])
        # component: statements 
        self.compile_statements(parent_node=subroutineBody_node)  
        # component: '}'
        self.consume(tkn_val=["}"], tkn_type="symbol", parent_node=subroutineBody_node) 
        #--------------------------------------------------------
        return
  
    #--------------------------------------------------------
    # recursive descent: varDec  
    #--------------------------------------------------------
    def compile_varDec(self, parent_node):  
        """ 'var' type varName (',' varName)* ';'  """  
        
        while self.current_token.ascii == "var":
            # new XML parent  
            varDec_node = ET.SubElement(parent_node, "varDec") 
            #--------------------------------------------------------
            self.symbol_table.compiling_state = "vars"
            self.symbol_table.update_subroutine_table(self.token_index, self.current_token.ascii, self.previous_token.ascii, self.next_token.ascii)
            # component: 'var'  
            self.consume(tkn_val=["var"], tkn_type="keyword", parent_node=varDec_node)
            # component: type
            self.symbol_table.update_subroutine_table(self.token_index, self.current_token.ascii, self.previous_token.ascii, self.next_token.ascii)  
            self.compile_type(parent_node=varDec_node) 
            # component: varName
            self.symbol_table.update_subroutine_table(self.token_index, self.current_token.ascii, self.previous_token.ascii, self.next_token.ascii)
            self.compile_varName(parent_node=varDec_node)  
            while self.current_token.ascii == ',':
                # component: ',' 
                self.consume(tkn_val=[","], tkn_type="symbol", parent_node=varDec_node)
                # component: varName
                self.symbol_table.update_subroutine_table(self.token_index, self.current_token.ascii, self.previous_token.ascii, self.next_token.ascii)
                self.compile_varName(parent_node=varDec_node)
            # component: ';'
            self.consume(tkn_val=[";"], tkn_type="symbol", parent_node=varDec_node)
        #--------------------------------------------------------
        return
    
    #--------------------------------------------------------
    # recursive descent: statements  
    #--------------------------------------------------------
    def compile_statements(self, parent_node):   
        """ statement*  """ 
         
        # new XML parent 
        statements_node = ET.SubElement(parent_node, "statements")
        #-------------------------------------------------------- 
        while self.current_token.ascii in ["let", "if", "while", "do", "return"]:
            self.compile_statement(parent_node=statements_node)  
        #--------------------------------------------------------
        return
     
    #--------------------------------------------------------
    # recursive descent: statement 
    #--------------------------------------------------------
    def compile_statement(self, parent_node):   
        """ letStatement | ifStatement | whileStatement | doStatement | returnStatement """

        if self.current_token.ascii == "let": self.compile_letStatement(parent_node=parent_node)   
        elif self.current_token.ascii == "if": self.compile_ifStatement(parent_node=parent_node)  
        elif self.current_token.ascii == "while": self.compile_whileStatement(parent_node=parent_node)  
        elif self.current_token.ascii == "do": self.compile_doStatement(parent_node=parent_node)   
        elif self.current_token.ascii == "return": self.compile_returnStatement(parent_node=parent_node) 
        return  
     
    #--------------------------------------------------------
    # recursive descent: letStatement 
    #--------------------------------------------------------
    def compile_letStatement(self, parent_node):    
        """ 'let' varName ('[' expression ']')? '=' expression ';' """

        # new XML parent 
        letStatement_node = ET.SubElement(parent_node, "letStatement")
        #--------------------------------------------------------
        # component: 'let'  
        self.consume(tkn_val=["let"], tkn_type="keyword", parent_node=letStatement_node)
        # component:varName ('[' expression ']')?
        if self.next_token.ascii == "[": 
            token = self.token_list[self.token_index]
            self.compile_varName(parent_node=letStatement_node) # component: varName  
            # component: '['
            self.consume(tkn_val=["["], tkn_type="symbol", parent_node=letStatement_node) 
            # component: expression 
            self.compile_expression(parent_node=letStatement_node)  
            # component: ']'   
            self.consume(tkn_val=["]"], tkn_type="symbol", parent_node=letStatement_node) 
            self.VMwriter.writePush(token=token)  
            self.VMwriter.WriteArithmetic("+")  
            Array_status = True
        # component: subroutineCall     
        else: 
            Array_status = False
            token = self.token_list[self.token_index]
            self.compile_varName(parent_node=letStatement_node)  
        
        # component: '=' 
        self.consume(tkn_val=["="], tkn_type="symbol", parent_node=letStatement_node) 
        # component: 'expression'
        self.compile_expression(parent_node=letStatement_node)
        # component: component: ';'   
        self.consume(tkn_val=[";"], tkn_type="symbol", parent_node=letStatement_node)
        if Array_status:
            self.VMwriter.writePop(segment="temp", index=0)  # pop the expression into a temp 
            self.VMwriter.writePop(segment="pointer", index=1) # store the topmost stack element in RAM[addr]
            self.VMwriter.writePush(segment="temp", index=0) 
            self.VMwriter.writePop(segment="that", index=0)
        else:
            self.VMwriter.writePop(token=token)   
        #-------------------------------------------------------- 
        return
    
    #--------------------------------------------------------
    # recursive descent: doStatement
    #--------------------------------------------------------
    def compile_doStatement(self, parent_node):  
        """ 'do' subroutineCall ';'  """ 
    
        # new XML parent   
        doStatement_node = ET.SubElement(parent_node, "doStatement")
        #--------------------------------------------------------
        # component: 'do'
        self.consume(tkn_val=["do"], tkn_type="keyword", parent_node=doStatement_node) 
        # subroutineCall 
        self.compile_subroutineCall(parent_node=doStatement_node)   
        # component: ';' 
        self.consume(tkn_val=[";"], tkn_type="symbol", parent_node=doStatement_node)
        #--------------------------------------------------------
        self.VMwriter.writePop(segment="temp", index=0) # return a pop temp    
        return 
    
    #--------------------------------------------------------
    # recursive descent: returnStatement
    #--------------------------------------------------------
    def compile_returnStatement(self, parent_node): 
        """ 'return' expression? ';'  """ 

        # new XML parent 
        returnStatement_node = ET.SubElement(parent_node, "returnStatement")
        #--------------------------------------------------------
        # component: 'return' 
        self.consume(tkn_val=["return"], tkn_type="keyword", parent_node=returnStatement_node)
        # component: expression? 
        if not self.current_token.ascii == ";": self.compile_expression(returnStatement_node) 
        self.VMwriter.writeReturn(self.symbol_table.subroutine_type) 
        # component: ';'   
        self.consume(tkn_val=[";"], tkn_type="symbol", parent_node=returnStatement_node)
        #--------------------------------------------------------
        return 
     
    #--------------------------------------------------------
    # recursive descent: ifStatement
    #--------------------------------------------------------
    def compile_ifStatement(self, parent_node): 
        """ 'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )? """
        if_count = 0
        # new XML parent  
        ifStatement_node = ET.SubElement(parent_node, "ifStatement")
        #--------------------------------------------------------
        # component: 'if' '(' expression ')' '{' statements '}' 
        # component: 'if' 
        self.VMwriter.num_functions["if"] += 1  
        self.consume(tkn_val=["if"], tkn_type="keyword", parent_node=ifStatement_node)
        # component: '('
        self.consume(tkn_val=["("], tkn_type="symbol", parent_node=ifStatement_node)
        # component: expression
        self.compile_expression(parent_node=ifStatement_node) 
        # component: ')'
        self.VMwriter.WriteIf(label="IF_TRUE", function="if")
        self.VMwriter.WriteGoto(label="IF_FALSE", function="if") 
        self.consume(tkn_val=[")"], tkn_type="symbol", parent_node=ifStatement_node)
        # component: '{'
        self.consume(tkn_val=["{"], tkn_type="symbol", parent_node=ifStatement_node)
        self.VMwriter.WriteLabel(label="IF_TRUE", function="if")
        # component: 'statements'
        if self.current_token.ascii =="if": if_count += 1
        self.compile_statements(parent_node=ifStatement_node)  
        # component: '}'  
        self.consume(tkn_val=["}"], tkn_type="symbol", parent_node=ifStatement_node)
        self.VMwriter.WriteGoto(label="IF_END",function="if", count=if_count)  
        self.VMwriter.WriteLabel(label="IF_FALSE", function="if", count=if_count)   
        # component: ( 'else' '{' statements '}' )?
        if self.current_token.ascii == "else": 
            # component: 'else'
            self.consume(tkn_val=["else"], tkn_type="keyword", parent_node=ifStatement_node)
            # component: '{'
            self.consume(tkn_val=["{"], tkn_type="symbol", parent_node=ifStatement_node)
            # component: 'statements'
            if self.current_token.ascii =="if": if_count += 1
            self.compile_statements(parent_node=ifStatement_node)  
            # component: '}'
            self.consume(tkn_val=["}"], tkn_type="symbol", parent_node=ifStatement_node)
        #--------------------------------------------------------
        self.VMwriter.WriteLabel(label="IF_END", function="if",count=if_count) 
        return if_count
    
    #--------------------------------------------------------
    # recursive descent: whileStatement 
    #--------------------------------------------------------
    def compile_whileStatement(self, parent_node): 
        """ 'while' '(' expression ')' '{' statements '}'  """ 
        while_count = 0
        # new XML parent  
        whileStatement_node = ET.SubElement(parent_node, "whileStatement") 
        #--------------------------------------------------------
        # component: 'while'
        self.VMwriter.num_functions["while"] += 1   
        self.VMwriter.WriteLabel(label="WHILE_EXP",function="while")
        self.consume(tkn_val=["while"], tkn_type="keyword", parent_node=whileStatement_node)
        # component: '('
        self.consume(tkn_val=["("], tkn_type="symbol", parent_node=whileStatement_node)
        # component: expression  
        self.compile_expression(whileStatement_node) 
        # component: ')'
        self.VMwriter.WriteArithmetic("~")
        self.VMwriter.WriteIf(label="WHILE_END",function="while",count=while_count)      
        self.consume(tkn_val=[")"], tkn_type="symbol", parent_node=whileStatement_node)
        # component: '{' 
        self.consume(tkn_val=["{"], tkn_type="symbol", parent_node=whileStatement_node)
        # component: 'statements'
        if self.current_token.ascii =="while": while_count += 1
        self.compile_statements(whileStatement_node)     
        # component: '}'
        self.consume(tkn_val=["}"], tkn_type="symbol", parent_node=whileStatement_node)
        #--------------------------------------------------------
        self.VMwriter.WriteGoto(label="WHILE_EXP",function="while", count=while_count) 
        self.VMwriter.WriteLabel(label="WHILE_END",function="while",count=while_count)  
        return while_count 
     
    #--------------------------------------------------------
    # recursive descent: expression  
    #--------------------------------------------------------
    def compile_expression(self, parent_node):   
        """ term (op term)* """
        term_count = 0
        neg =  False
        # new XML parent 
        expression_node = ET.SubElement(parent_node, "expression") 
        #--------------------------------------------------------
       
        if self.current_token.ascii in self.lexer.symbols.unary_op and self.previous_token.ascii in ["=" , ",",", ", "(" ]:
            operator = self.current_token.ascii
            # component: term    
            self.compile_term(parent_node=expression_node)    
            if operator == "-": self.VMwriter.WriteArithmetic(operator="neg", term_count=term_count) 
            else: self.VMwriter.WriteArithmetic(operator=operator, term_count=term_count)
        else: 
            # component: term
            self.compile_term(parent_node=expression_node)  
            term_count += 1
        # component: term (op term)*
        while (self.current_token.ascii in self.lexer.symbols.operator): 
            #--------------------------------------------------------
            f = open("permanent_variables.txt","w+")
            f.write(self.current_token.ascii) # write permanent variable
            f = open("permanent_variables.txt","r")  
            operator = f.read() # save permanent variable
            f = open("permanent_variables.txt","w+") 
            f.seek(0)
            f.truncate()
            f.close() # delete file contents and close file
            #--------------------------------------------------------
            # component: component: op  
            self.consume(tkn_val=self.lexer.symbols.operator, tkn_type="symbol", parent_node=expression_node)
            # component: term  
            self.compile_term(parent_node=expression_node)
            term_count += 1
            self.VMwriter.WriteArithmetic(operator=operator, term_count=term_count) 
        #-------------------------------------------------------- 
        return  
   
    #--------------------------------------------------------
    # recursive descent: expressionList 
    #--------------------------------------------------------
    def compile_expressionList(self, empty, parent_node):   
        """ (expression (',' expression)* )? """
        expression_counter = 0
        # new XML parent 
        if empty:expressionList_node = ET.SubElement(parent_node, "expressionList").text = " " + "\n"
        if not empty:expressionList_node = ET.SubElement(parent_node, "expressionList")
        #--------------------------------------------------------   
        while not (self.current_token.ascii in [")"]): 
                # component: expression  
                self.compile_expression(parent_node=expressionList_node) 
                expression_counter += 1
                # component: , 
                self.consume(tkn_val=[", ", ","], tkn_type="symbol", parent_node=expressionList_node) 
        #--------------------------------------------------------
        return expression_counter

    #--------------------------------------------------------
    # recursive descent: term 
    #--------------------------------------------------------
    def compile_term(self, parent_node):     
        """
        integerConstant | stringConstant | keywordConstant | varName |
        varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term 
        """

        # new XML parent     
        if not self.current_token.ascii in [")", "]"]:  
            term_node = ET.SubElement(parent_node, "term")
        #-------------------------------------------------------- 

        if self.current_token.type == "integerConstant":  # component: integerConstant
            self.VMwriter.writePush(self.current_token, segment=None, index=None) 
            return self.consume(tkn_val=[], tkn_type="integerConstant", parent_node=term_node) 

        elif self.current_token.type == "stringConstant": # component: stringConstant 
            self.VMwriter.writePush(self.current_token, segment=None, index=None)  
            return self.consume(tkn_val=[], tkn_type="stringConstant", parent_node=term_node) 

        elif self.current_token.ascii in self.lexer.symbols.keyword_constant: # component: keywordConstant
            self.VMwriter.writePush(self.current_token, segment=None, index=None)  
            return self.consume(tkn_val=[], tkn_type="keyword", parent_node=term_node)   

        elif self.current_token.type == "identifier":  
            # component: varName '[' expression ']'
            if self.next_token.ascii == "[": 
                token = self.token_list[self.token_index]
                self.compile_varName(parent_node=term_node) # component: varName  
                # component: '['
                self.consume(tkn_val=["["], tkn_type="symbol", parent_node=term_node) 
                # component: expression 
                self.compile_expression(parent_node=term_node) 
                # component: ']'  
                self.consume(tkn_val=["]"], tkn_type="symbol", parent_node=term_node) 
                self.VMwriter.writePush(token=token)  
                self.VMwriter.WriteArithmetic("+")  
                self.VMwriter.writePop(segment="pointer", index=1) # store the topmost stack element in RAM[addr]
                self.VMwriter.writePush(segment="that", index=0)
                return

            # component: subroutineCall    
            elif self.next_token.ascii == "(" or self.next_token.ascii == ".": 
                return self.compile_subroutineCall(parent_node=term_node) # subroutineCall
            
            # component: varName  
            else: 
                self.VMwriter.writePush(self.current_token) 
                return self.compile_varName(parent_node=term_node)
  
        elif self.current_token.ascii == "(":# '(' expression ')' 
            self.consume(tkn_val=["("], tkn_type="symbol", parent_node=term_node) # component: '('
            self.compile_expression(parent_node=term_node) # component: expression 
            self.consume(tkn_val=[")"], tkn_type="symbol", parent_node=term_node) # component: ')'
            return
            
        # component: unaryOp term
        elif self.current_token.ascii in self.lexer.symbols.unary_op: 
            self.consume(tkn_val=['-','~'], tkn_type="symbol", parent_node=term_node) # component: unaryOp   
            self.compile_term(parent_node=term_node) # component: term
            return 
        #--------------------------------------------------------  
        return

    #--------------------------------------------------------
    # recursive descent: subroutineCall
    #--------------------------------------------------------
    def compile_subroutineCall(self, parent_node):   
        """
        subroutineName '(' expressionList ')' | ( className | varName) '.' subroutineName
        '(' expressionList ')'  
        """ 

        # component: subroutineName '(' expressionList ')'
        if self.next_token.ascii == "(": 
            #--------------------------------------------------------
            f = open("permanent_variables.txt","w+")
            f.write(self.current_token.ascii) # write permanent variable
            f = open("permanent_variables.txt","r")  
            subroutineName = f.read() # save permanent variable
            f = open("permanent_variables.txt","w+") 
            f.seek(0)
            f.truncate()
            f.close() # delete file contents and close file
            #--------------------------------------------------------
            # component: subroutineName 
            self.compile_subroutineName(parent_node=parent_node)
            # check if list is empty (print space with closing tag if empty)
            if ( self.current_token.ascii == "(" ) and ( self.next_token.ascii == ")" ):
                # component: '('
                self.consume(tkn_val=["("], tkn_type="symbol", parent_node=parent_node)
                # component: expressionList
                nArgs = self.compile_expressionList(empty=True, parent_node=parent_node) 
                # component: ')'   
                self.consume(tkn_val=[")"], tkn_type="symbol", parent_node=parent_node)
                self.VMwriter.writeCall(subroutineName=subroutineName, nArgs=nArgs)
            else:
                # component: '('
                self.consume(tkn_val=["("], tkn_type="symbol", parent_node=parent_node)
                # component: expressionList
                nArgs = self.compile_expressionList(empty=False, parent_node=parent_node) 
                # component: ')'   
                self.consume(tkn_val=[")"], tkn_type="symbol", parent_node=parent_node)
                self.VMwriter.writeCall(subroutineName=subroutineName, nArgs=nArgs)
      
        # component: ( className | varName) '.' subroutineName '(' expressionList ')'   
        if self.next_token.ascii == ".":
            #--------------------------------------------------------
            f = open("permanent_variables.txt","w+")
            f.write(self.current_token.ascii) # write permanent variable
            f = open("permanent_variables.txt","r")  
            className = f.read() # save permanent variable
            f = open("permanent_variables.txt","w+") 
            f.seek(0)
            f.truncate()
            f.close() # delete file contents and close file
            #--------------------------------------------------------
            # component: ( className | varName)
            self.consume(tkn_val=[], tkn_type="identifier", parent_node=parent_node)
            # component: '.'
            self.consume(tkn_val=["."], tkn_type="symbol", parent_node=parent_node)
            #--------------------------------------------------------
            f = open("permanent_variables.txt","w+")
            f.write(self.current_token.ascii) # write permanent variable
            f = open("permanent_variables.txt","r")  
            subroutineName = f.read() # save permanent variable
            f = open("permanent_variables.txt","w+") 
            f.seek(0) 
            f.truncate()
            f.close() # delete file contents and close file
            #--------------------------------------------------------
            # component: subroutineName
            self.compile_subroutineName(parent_node=parent_node) 
            
            # check if list is empty (print space with closing tag if empty)
            if ( self.current_token.ascii == "(" ) and ( self.next_token.ascii == ")" ):
                # component: '('
                self.consume(tkn_val=["("], tkn_type="symbol", parent_node=parent_node)
                # component: expressionList
                nArgs = self.compile_expressionList(empty=True, parent_node=parent_node) 
                # component: ')'  
                self.consume(tkn_val=[")"], tkn_type="symbol", parent_node=parent_node)
                self.VMwriter.writeCall(className=className, subroutineName=subroutineName, nArgs=nArgs)
            else:  
                # component: '('
                self.consume(tkn_val=["("], tkn_type="symbol", parent_node=parent_node)
                # component: expressionList
                nArgs = self.compile_expressionList(empty=False,parent_node=parent_node) 
                # component: ')'  
                self.consume(tkn_val=[")"], tkn_type="symbol", parent_node=parent_node)
                self.VMwriter.writeCall(className=className, subroutineName=subroutineName, nArgs=nArgs) 
        #--------------------------------------------------------
        return  
        
     

        
        


