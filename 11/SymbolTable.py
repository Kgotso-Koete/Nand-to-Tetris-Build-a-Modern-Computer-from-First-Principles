class SymbolTable:
    """ A symbol table that associates names with information needed for Jack compilation """
    def __init__(self):
        self.class_table = None
        self.class_name = None
        self.subroutine_table = None
        self.subroutine_name = None
        self.subroutine_type = None
        self.subroutine_kind = None
        self.compiling_state = ""
        self.var_count = {"static": 0, "field": 0, "argument": 0, "var": 0}
        self.current_table_data = {} #current_table_data = {"kind": , "type": , "name" }
    
    #--------------------------------------------------------
    # class 
    #--------------------------------------------------------
    def new_class_scope(self, class_name):
        """ Starts a new class scope"""
        self.class_table = {}
        self.class_name = class_name
        self.var_count["static"] = 0
        self.var_count["field"] = 0
        return 
    
    def define_class(self, name=None, kind=None, name_type=None):
        """ Defines a new identifier of a given name, type, and kind and assigns it a running index """
        if name not in self.class_table:
            self.class_table[name] = {}
            self.class_table[name]["type"] = name_type
            self.class_table[name]["kind"] = kind
            self.class_table[name]["kind_index"] = self.var_count[kind] 
            self.var_count[kind] += 1
            #print("Class symbol table items...")
            #print(self.class_table.items()) 
        return
    
    def update_class_table(self, token_index, current_tkn_val, previous_tkn_val, next_tkn_val):
        if token_index > 1:
            # current_table_data = {"kind": , "type": , "name" }
            if current_tkn_val in ['static', 'field']: 
                self.current_table_data['kind'] = current_tkn_val
            if previous_tkn_val in ['static', 'field']:
                self.current_table_data['type'] = current_tkn_val
            if next_tkn_val in [',', ';']:
                name = current_tkn_val
                kind = self.current_table_data['kind']
                name_type = self.current_table_data['type']
                self.define_class(name=name, kind=kind, name_type=name_type)
        return
    
    #--------------------------------------------------------
    # subroutines 
    #--------------------------------------------------------
    def new_subroutine_scope(self, subroutine_kind, subroutine_type , subroutine_name): 
        """ Starts a new subroutine scope (i.e. erases all names in the previous subroutine’s scope.)  """
        self.subroutine_table = {}
        self.subroutine_kind = subroutine_kind 
        self.subroutine_name = subroutine_name
        self.subroutine_type = subroutine_type 
        self.var_count["argument"] = 0
        self.var_count["var"] = 0
        # init the 'this argument'
        if self.subroutine_kind in ["constructor", "method"]:
            name = "this"
            kind = "argument"
            name_type = self.class_name 
            self.define_subroutine(name=name, kind=kind, name_type=name_type)
        return
 
    def define_subroutine(self, name=None, kind=None, name_type=None):
        """ Defines a new identifier of a given name, type, and kind and assigns it a running index """
        if name not in self.subroutine_table:
            self.subroutine_table[name] = {}
            self.subroutine_table[name]["type"] = name_type
            self.subroutine_table[name]["kind"] = kind
            self.subroutine_table[name]["kind_index"] = self.var_count[kind] 
            self.var_count[kind] += 1
            #print("Subroutine symbol table items...") 
            #print(self.subroutine_table.items())
        return 
      
    def update_subroutine_table(self, token_index, current_tkn_val, previous_tkn_val, next_tkn_val):
        if token_index > 1:
            # current_table_data = {"kind": , "type": , "name" }
            if self.compiling_state == "args":
                if next_tkn_val in [',',', ', ')']:
                    self.current_table_data['type'] = previous_tkn_val
                    self.current_table_data['kind'] = "argument"
                    # add new entry
                    name = current_tkn_val
                    kind = self.current_table_data['kind'] 
                    name_type = self.current_table_data['type']
                    self.define_subroutine(name=name, kind=kind, name_type=name_type)
            
            if self.compiling_state == "vars":
                if current_tkn_val in ['var']: 
                    self.current_table_data['kind'] = current_tkn_val
                if previous_tkn_val in ['var']:
                    self.current_table_data['type'] = current_tkn_val
                if next_tkn_val in [',', ';']:
                    name = current_tkn_val
                    kind = self.current_table_data['kind']
                    name_type = self.current_table_data['type']
                    self.define_subroutine(name=name, kind=kind, name_type=name_type)
        return 
        
    
    
    