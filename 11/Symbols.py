class Symbols: 
    """ stores standard Jack symbols"""
    def __init__(self):  

        #--------------------------------------------------------
        # Lexical elements
        #--------------------------------------------------------
        self.keyword = ['class', 'constructor', 'function', 'method', 'field', 
                        'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 
                        'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'] 
        
        self.symbol = ['{', '}', '(', ')', '[', ']', '.', ', ', ';', '+', '-', '*',
                        '/', '&', '|', '<', '>', '=', '~', ',' ] 
        
        self.integerConstant = list(range(0, 32767 + 1))   
        
        #--------------------------------------------------------
        # Other useful parsing grammars
        #-------------------------------------------------------- 
        self.operator = ['+', '-', '*', '/', '&', '|', '<', '>', '=' ] 
        self.type = ['int', 'char', 'boolean']
        self.unary_op = ['-','~'] 
        self.keyword_constant = ['true', 'false', 'null', 'this' ]  

          