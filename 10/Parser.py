import xml.etree.ElementTree as ET     
from Scanner import *
from Lexer import *
import sys
import itertools
 
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
            self.consume(tkn_val=[], tkn_type="keyword", parent_node=classVarDec_node)  
            # component: type
            self.compile_type(parent_node=classVarDec_node) 
            
            while ";" not in self.current_token.ascii:  
                # component: varName 
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
 
        # new XML parent 
        subroutineDec_node = ET.SubElement(parent_node, "subroutineDec")  
        #--------------------------------------------------------
        # component: ('constructor' | 'function' | 'method')
        self.consume(tkn_val=['constructor', 'function', 'method'], tkn_type="keyword", parent_node=subroutineDec_node) 

        # component: ('void' | type)  
        if self.current_token.ascii == "void":
            self.consume(tkn_val=["void"], tkn_type="keyword", parent_node=subroutineDec_node) 
        else: 
            self.compile_type(parent_node=subroutineDec_node) 
        
        # component: subroutineName 
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
            # component: 'var'  
            self.consume(tkn_val=["var"], tkn_type="keyword", parent_node=varDec_node)
            # component: type    
            self.compile_type(parent_node=varDec_node) 
            # component: varName
            self.compile_varName(parent_node=varDec_node)  
            while self.current_token.ascii == ',':
                # component: ','
                self.consume(tkn_val=[","], tkn_type="symbol", parent_node=varDec_node)
                # component: varName
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
            self.compile_varName(parent_node=letStatement_node) # component: varName  
            # component: '['
            self.consume(tkn_val=["["], tkn_type="symbol", parent_node=letStatement_node) 
            # component: expression 
            self.compile_expression(parent_node=letStatement_node)  
            # component: ']'   
            self.consume(tkn_val=["]"], tkn_type="symbol", parent_node=letStatement_node) 
        # component: subroutineCall     
        else: self.compile_varName(parent_node=letStatement_node) 
        
        # component: '=' 
        self.consume(tkn_val=["="], tkn_type="symbol", parent_node=letStatement_node) 
        # component: 'expression'
        self.compile_expression(parent_node=letStatement_node)  
        # component: component: ';'  
        self.consume(tkn_val=[";"], tkn_type="symbol", parent_node=letStatement_node)
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
        # component: ';'   
        self.consume(tkn_val=[";"], tkn_type="symbol", parent_node=returnStatement_node)
        #--------------------------------------------------------
        return 
     
    #--------------------------------------------------------
    # recursive descent: ifStatement
    #--------------------------------------------------------
    def compile_ifStatement(self, parent_node): 
        """ 'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )? """

        # new XML parent  
        ifStatement_node = ET.SubElement(parent_node, "ifStatement")
        #--------------------------------------------------------
        # component: 'if' '(' expression ')' '{' statements '}' 
        # component: 'if' 
        self.consume(tkn_val=["if"], tkn_type="keyword", parent_node=ifStatement_node)
        # component: '('
        self.consume(tkn_val=["("], tkn_type="symbol", parent_node=ifStatement_node)
        # component: expression
        self.compile_expression(parent_node=ifStatement_node) 
        # component: ')'
        self.consume(tkn_val=[")"], tkn_type="symbol", parent_node=ifStatement_node)
        # component: '{'
        self.consume(tkn_val=["{"], tkn_type="symbol", parent_node=ifStatement_node)
        # component: 'statements'
        self.compile_statements(parent_node=ifStatement_node) 
        # component: '}' 
        self.consume(tkn_val=["}"], tkn_type="symbol", parent_node=ifStatement_node)
        # component: ( 'else' '{' statements '}' )?
        if self.current_token.ascii == "else": 
            # component: 'else'
            self.consume(tkn_val=["else"], tkn_type="keyword", parent_node=ifStatement_node)
            # component: '{'
            self.consume(tkn_val=["{"], tkn_type="symbol", parent_node=ifStatement_node)
            # component: 'statements'
            self.compile_statements(parent_node=ifStatement_node) 
            # component: '}'
            self.consume(tkn_val=["}"], tkn_type="symbol", parent_node=ifStatement_node)
        #--------------------------------------------------------
        return
    
    #--------------------------------------------------------
    # recursive descent: whileStatement 
    #--------------------------------------------------------
    def compile_whileStatement(self, parent_node): 
        """ 'while' '(' expression ')' '{' statements '}'  """ 

        # new XML parent 
        whileStatement_node = ET.SubElement(parent_node, "whileStatement") 
        #--------------------------------------------------------
        # component: 'while'
        self.consume(tkn_val=["while"], tkn_type="keyword", parent_node=whileStatement_node)
        # component: '('
        self.consume(tkn_val=["("], tkn_type="symbol", parent_node=whileStatement_node)
        # component: expression
        self.compile_expression(whileStatement_node) 
        # component: ')'
        self.consume(tkn_val=[")"], tkn_type="symbol", parent_node=whileStatement_node)
        # component: '{' 
        self.consume(tkn_val=["{"], tkn_type="symbol", parent_node=whileStatement_node)
        # component: 'statements'
        self.compile_statements(whileStatement_node) 
        # component: '}'
        self.consume(tkn_val=["}"], tkn_type="symbol", parent_node=whileStatement_node)
        #--------------------------------------------------------
        return
     
    #--------------------------------------------------------
    # recursive descent: expression
    #--------------------------------------------------------
    def compile_expression(self, parent_node):   
        """ term (op term)* """

        # new XML parent 
        expression_node = ET.SubElement(parent_node, "expression") 
        #--------------------------------------------------------
        # component: term (op term)*
        while not (self.current_token.ascii in [";", "=",")", ",",", "]): 
            # component: term
            self.compile_term(parent_node=expression_node)  
            # component: component: op  
            self.consume(tkn_val=self.lexer.symbols.operator, tkn_type="symbol", parent_node=expression_node)
            # GETTING OUT OF THE LOOP: use lookahead (self.next_token) 
            if self.next_token.ascii in [";", "=",")", ",",", "]:   
                # component: term  
                self.compile_term(parent_node=expression_node)  
                 # component: component: op    
                self.consume(tkn_val=self.lexer.symbols.operator, tkn_type="symbol", parent_node=expression_node)
                break  
        #-------------------------------------------------------- 
        return  
 
    #--------------------------------------------------------
    # recursive descent: expressionList 
    #--------------------------------------------------------
    def compile_expressionList(self, empty, parent_node):   
        """ (expression (',' expression)* )? """

        # new XML parent 
        if empty:expressionList_node = ET.SubElement(parent_node, "expressionList").text = " " + "\n"
        if not empty:expressionList_node = ET.SubElement(parent_node, "expressionList")
        #--------------------------------------------------------   
        while not (self.current_token.ascii in [")"]): 
                # component: expression  
                self.compile_expression(parent_node=expressionList_node) 
                # component: , 
                self.consume(tkn_val=[", ", ","], tkn_type="symbol", parent_node=expressionList_node) 
        #--------------------------------------------------------
        return

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
            return self.consume(tkn_val=[], tkn_type="integerConstant", parent_node=term_node) 

        elif self.current_token.type == "stringConstant": # component: stringConstant 
            return self.consume(tkn_val=[], tkn_type="stringConstant", parent_node=term_node) 

        elif self.current_token.ascii in self.lexer.symbols.keyword_constant: # component: keywordConstant
            return self.consume(tkn_val=[], tkn_type="keyword", parent_node=term_node)   

        elif self.current_token.type == "identifier":  
            # component: varName '[' expression ']'
            if self.next_token.ascii == "[": 
                self.compile_varName(parent_node=term_node) # component: varName  
                # component: '['
                self.consume(tkn_val=["["], tkn_type="symbol", parent_node=term_node) 
                # component: expression 
                self.compile_expression(parent_node=term_node) 
                # component: ']'  
                self.consume(tkn_val=["]"], tkn_type="symbol", parent_node=term_node) 
                return

            # component: subroutineCall    
            elif self.next_token.ascii == "(" or self.next_token.ascii == ".": 
                return self.compile_subroutineCall(parent_node=term_node) # subroutineCall
            
            # component: varName 
            else: return self.compile_varName(parent_node=term_node)
  
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
            # component: subroutineName
            self.compile_subroutineName(parent_node=parent_node)
            
            # check if list is empty (print space with closing tag if empty)
            if ( self.current_token.ascii == "(" ) and ( self.next_token.ascii == ")" ):
                # component: '('
                self.consume(tkn_val=["("], tkn_type="symbol", parent_node=parent_node)
                # component: expressionList
                self.compile_expressionList(empty=True, parent_node=parent_node) 
                # component: ')'   
                self.consume(tkn_val=[")"], tkn_type="symbol", parent_node=parent_node)
            else:
                # component: '('
                self.consume(tkn_val=["("], tkn_type="symbol", parent_node=parent_node)
                # component: expressionList
                self.compile_expressionList(empty=False, parent_node=parent_node) 
                # component: ')'   
                self.consume(tkn_val=[")"], tkn_type="symbol", parent_node=parent_node)

        # component: ( className | varName) '.' subroutineName '(' expressionList ')'   
        if self.next_token.ascii == ".":
            # component: ( className | varName)
            self.consume(tkn_val=[], tkn_type="identifier", parent_node=parent_node)
            # component: '.'
            self.consume(tkn_val=["."], tkn_type="symbol", parent_node=parent_node)
            # component: subroutineName
            self.compile_subroutineName(parent_node=parent_node) 
            
            # check if list is empty (print space with closing tag if empty)
            if ( self.current_token.ascii == "(" ) and ( self.next_token.ascii == ")" ):
                # component: '('
                self.consume(tkn_val=["("], tkn_type="symbol", parent_node=parent_node)
                # component: expressionList
                self.compile_expressionList(empty=True, parent_node=parent_node) 
                # component: ')'  
                self.consume(tkn_val=[")"], tkn_type="symbol", parent_node=parent_node)
            else:  
                # component: '('
                self.consume(tkn_val=["("], tkn_type="symbol", parent_node=parent_node)
                # component: expressionList
                self.compile_expressionList(empty=False,parent_node=parent_node) 
                # component: ')'  
                self.consume(tkn_val=[")"], tkn_type="symbol", parent_node=parent_node)
        #--------------------------------------------------------
        return  
        
     

        
        


