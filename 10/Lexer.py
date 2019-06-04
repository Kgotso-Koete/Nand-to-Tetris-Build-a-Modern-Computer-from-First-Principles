from Scanner import *
from Token import *
from Symbols import *
import re
   
class Lexer:
    """ A lexer for the Jack language """
   
    def __init__(self, source_text):
        self.scanner = Scanner(source_text) # initialize the scanner with the source_text
        self.scanner.file_read()
        self.symbols = Symbols() # initialise the Jack standard symbol table
        self.token_list = [] 
        self.endmark = "\0"
 
    def get_token_types(self): 
        """ Construct and return a list of tokens and their types """
 
        # With help from: https://deplinenoise.wordpress.com/2012/01/04/python-tip-regex-based-tokenizer/
        SCANNER = re.compile(r'''
        (\s+) |                      # whitespace
        (//)[^\n]* |                 # comments
        0[xX]([0-9A-Fa-f]+) |        # hexadecimal integer literals
        (\d+) |                      # integer literals
        (<<|>>) |                    # multi-char punctuation
        ([][(){}<>=,;:*+-/|&~]) |    # punctuation 
        ([A-Za-z_][A-Za-z0-9_]*) |   # identifiers
        """(.*?)""" |                # multi-line string literal
        "((?:[^"\n\\]|\\.)*)" |      # regular string literal
        (.) |                        # an error!
        ''', re.DOTALL | re.VERBOSE)
             
        for match in re.finditer(SCANNER, self.scanner.modified_source_text): 
             
            (space, comment, hexint, integer, mpunct, 
            punct, word, mstringlit, stringlit, badchar) = match.groups()
                
            if word: 
                #-------------------------------------------------------------------
                # check if word is an keyword
                #-------------------------------------------------------------------
                if word in self.symbols.keyword:  
                    keyword_token = Token(word, "keyword") 
                    self.token_list.append(keyword_token)
                #-------------------------------------------------------------------
                # check if word is an identifier
                #-------------------------------------------------------------------
                else:
                    identifier_token = Token(word, "identifier")  
                    self.token_list.append(identifier_token)
            #-------------------------------------------------------------------
            # check if word is an integerConstant
            #-------------------------------------------------------------------
            if integer:
                Int_token = Token(integer, "integerConstant") 
                self.token_list.append(Int_token)
            #-------------------------------------------------------------------
            # check if word is an symbol  
            #-------------------------------------------------------------------
            if punct:  
                symbol_token = Token(punct, "symbol") 
                self.token_list.append(symbol_token)
            #-------------------------------------------------------------------
            # check if word is an stringConstant
            #------------------------------------------------------------------- 
            if stringlit: 
                string_token = Token(stringlit, "stringConstant") 
                self.token_list.append(string_token)  
        #-------------------------------------------------------------------
        # append EOF token
        #-------------------------------------------------------------------         
        EOF_token = Token(self.endmark, "EOF") 
        self.token_list.append(EOF_token) 
         
        return self.token_list    
    
    def print_tokens(self): 
        for t in self.token_list: 
            print("|", "Token val: ", t.ascii, " | ", "Token type: ", t.type, " |")  


        

        
        
	