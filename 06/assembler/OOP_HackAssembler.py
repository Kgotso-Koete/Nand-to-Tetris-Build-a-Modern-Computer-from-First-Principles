# Uses python3
import re

class Assembler:

    def __init__(self):
        # I/O data structures
        self.input_file = None # input file used to parse commands
        self.output_file = None  # output file where binary code will be written

        # key data structures
        self.input_data = None  # commands parsed and captured in list format
        self.translation_dict = None # standard hack to binary translator
        self.symbol_dict = None
        self.output_dict = None
        
        # secondary variables
        self.non_Lcommand_position = 0
        self.assigned_register = 15
        

    def parser(self, input_file):
        """
        Purpose: Unpacks each underlying instructin into it's underlying fields
        Input:Text file containing instuctions
        Output: Data structure containing fields
        """
        # source: https://stackoverflow.com/a/52732203/6556133
        source_re = r'(?m)^ *(.*?) *(?:/.*)?$'  # Regex each line from file without line breaks 
        # open file
        with open(input_file, 'r') as infile:
            source = infile.read().strip()
            match = re.sub(source_re , r'\1', source)
        self.input_data = match.split() # put data in a list

        return 
    
    def make_translation_dict(self):
        """
        Purpose: Makes a standard symbol tabe for reference in creating
        Input: Uninitiated translation dictionary with fields
        Output: Translation dictionary with binary translation values
        """
        # translation dictionary for a-bit of “ixxaccccccdddjjj”
        a_dict = {'0':'0', '1':'0', '-1':'0', 'D':'0', 'A':'0', '!D':'0', '!A':'0', '-D':'0', '-A':'0', 'D+1':'0', 'A+1':'0', 'D-1':'0',
                  'A-1':'0', 'D+A':'0', 'D-A':'0', 'A-D':'0', 'D&A':'0', 'D|A':'0', 'M':'1', '!M':'1', '-M':'1', 'M+1':'1', 'M-1':'1',
                  'D+M':'1', 'D-M':'1', 'M-D':'1', 'D&M':'1', 'D|M':'1' }
        
        # translation dictionary for c1 to c6-bit of “ixxaccccccdddjjj”
        comp_dict = {'0':'101010', '1':'111111', '-1':'111010', 'D':'001100', 'A':'110000', '!D':'001101', '!A':'110001', '-D':'001111',
                     '-A':'110011', 'D+1':'011111', 'A+1':'110111', 'D-1':'001110', 'A-1':'110010', 'D+A':'000010', 'D-A':'010011',
                     'A-D':'000111', 'D&A':'000000', 'D|A':'010101', 'M':'110000', '!M':'110001', '-M':'110011', 'M+1':'110111',
                     'M-1':'110010', 'D+M':'000010', 'D-M':'010011', 'M-D':'000111', 'D&M':'000000', 'D|M':'010101'}
        
        # translation dictionary for destination-bits (d1,d2,d3) of “ixxaccccccdddjjj”
        dest_dict = {'null':'000', 'M':'001', 'D':'010', 'MD':'011', 'A':'100', 'AM':'101', 'AD':'110', 'AMD':'111'}
        # translation dictionary for destination-bits (d1,d2,d3) of “ixxaccccccdddjjj”
        jump_dict = {'null':'000', 'JGT':'001', 'JEQ':'010', 'JGE':'011','JLT':'100', 'JNE':'101','JLE':'110','JMP':'111'}
        # create the class translation dictionary
        self.translation_dict = {'a_dict': a_dict , 'comp_dict': comp_dict, 'dest_dict': dest_dict, 'jump_dict': jump_dict} 

        return

    def make_symbol_dict(self):
        """
        Purpose: Collects symbols in a table containing addresses
        Input: Unitiated symbol dictionary
        Output: Symbol dictionary initiatied with standard hack symbols
        """
        
        #creating the standard symbol table
        self.symbol_dict = {'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4, 'R0': 0, 'R1': 1, 'R2':2, 'R3': 3,
                            'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7, 'R8' : 8, 'R9' : 9, 'R10': 10, 'R11': 11, 'R12': 12,
                            'R13': 13, 'R14': 14, 'R15': 15, 'SCREEN': 16384, 'KBD': 24576}

        return 
    
    def is_number(self, n):
        try:
            float(n)   # Type-casting the string to `float`.
                    # If string is not a valid `float`, 
                    # it'll raise `ValueError` exception
        except ValueError:
            return False
        return True
    
    def make_output_dict(self, input_data): 
        """
        Purpose: Initialises the output dictionary
        Input: Empty output dictionary
        Output: Defined fields in output dictionary
        """
        # initialise dictionary
        self.output_dict = {}

        for i in range(len(input_data)):
            self.output_dict[i] = {}
            self.output_dict[i]['instruction'] = ''
            self.output_dict[i]['commandType'] = ''  # the type of the current command 
            self.output_dict[i]['symbol'] = '' # returns the symbol or decimal
            self.output_dict[i]['a-bit'] = ''
            self.output_dict[i]['dest'] = '' # returns the dest mnemonic in the current C-command for dest=comp;jump
            self.output_dict[i]['comp'] = '' # returns the comp mnemonic in the current C-command for dest=comp;jump
            self.output_dict[i]['jump'] = '' # returns the jump mnemonic in the current C-command for dest=comp;jump
            self.output_dict[i]['instruction_pointer'] = None
            self.output_dict[i]['binary_translation'] = ''
        
        return
    

    def command_type(self, i, line): 
        """
        Purpose: Determines if the instruction is an A, C or L command
        Input: Command position and command in input data list
        Output: Command classification
        """
        cmd_type = ''

        if line.startswith('@'):
           cmd_type = 'A' # for @Xxx where Xxx is either a symbol or a decimal number 
        elif line.startswith('('):
           cmd_type = 'L' # pseudo-command for (Xxx) where Xxx is a symbol.
        else:
            cmd_type = 'C' # for dest=comp;jump

        return cmd_type
    
    def get_instruction_number(self, i):
        """
        Purpose: Updates each instruction with the appropriate instruction number
        Input: Command list and index of current instruction
        Output: Updated command list with instruction numbers for each instruction
        """
        # add instruction numbers  
        
        if self.output_dict[i]['commandType'] == 'C': self.output_dict[i]['instruction_pointer'] = i
        if self.output_dict[i]['commandType'] == 'A': self.output_dict[i]['instruction_pointer'] = i
        if self.output_dict[i]['commandType'] == 'L': self.output_dict[i]['instruction_pointer'] = self.non_Lcommand_position  + 1
    
        return  
    
    def symbol_dict_first_update(self, i):
        """
        Purpose: Collects symbols in a table containing A and C addresses
        Input: Symbol dictionary and command list
        Output: Symbol dictionary and command list that includes symbol addresses for A and C commands
        """
        if self.output_dict[i]['commandType'] == 'L':
            if self.output_dict[i]['instruction'][1:-1] not in self.symbol_dict:
                self.symbol_dict[self.output_dict[i]['instruction'][1:-1]] = self.output_dict[i]['instruction_pointer']

        return
    

    def symbol_dict_second_update(self, i):
        """
        Purpose: Collects symbols in a table containing L addresses
        Input: Symbol dictionary and command list
        Output: Symbol dictionary and command list that includes symbol addresses for L commands
        """

        # update the symbol tables
        if self.output_dict[i]['commandType'] == 'A':
            if not self.is_number(self.output_dict[i]['instruction'].split("@")[1]):
                if self.output_dict[i]['instruction'].split("@")[1] not in self.symbol_dict:
                    self.symbol_dict[self.output_dict[i]['instruction'].split("@")[1]] =  self.assigned_register + 1
                    self.assigned_register += 1 

        return
        

    def update_output_dict(self): 
        """
        Purpose: Initialises the output dictionary
        Input: Empty output dictionary
        Output: Defined fields in output dictionary
        """
        # process output dictionary update
        for i in range(len(self.input_data)):
            # get instructions
            self.output_dict[i]['instruction'] = self.input_data[i]
            # get command types
            self.output_dict[i]['commandType'] = self.command_type(i, self.input_data[i])  # the type of the current command 
            # get instruction numbers 
            if  self.output_dict[i]['commandType'] == 'A' or  self.output_dict[i]['commandType'] == 'C':
                self.non_Lcommand_position += 1
            self.get_instruction_number(i)    
         
        return
    
    def get_symbol_value(self, i):
        """
        Purpose: Collects symbols in a table containing addresses
        Input:Symbol dictionary and command list
        Output: Symbol dictionary and command list that includes symbol addresses
        """
        
        # update the symbols values
        if self.output_dict[i]['commandType'] == 'A':
            # if the A instruction is a decimal number
            if self.is_number(self.output_dict[i]['instruction'].split("@")[1]):
                self.output_dict[i]['symbol'] = self.output_dict[i]['instruction'].split("@")[1]
            
            # if A instruction is not a decimal, then just make the decimal the symbol
            if not self.is_number(self.output_dict[i]['instruction'].split("@")[1]):
                temp = '(' +  self.output_dict[i]['instruction'].split("@")[1] + ')'
                if temp not in self.input_data:
                    self.output_dict[i]['symbol'] = self.symbol_dict[self.output_dict[i]['instruction'].split("@")[1]]  
                if temp in self.input_data:
                    self.output_dict[i]['symbol'] = self.symbol_dict[self.output_dict[i]['instruction'].split("@")[1]] - 1
            
        # if the instruction is a symbol
        if self.output_dict[i]['commandType'] == 'L':  
            if self.output_dict[i]['instruction'][1:-1] in self.symbol_dict:
                self.output_dict[i]['symbol'] = self.symbol_dict[self.output_dict[i]['instruction'][1:-1]] 

        return
    
    def get_code(self, i):
        """
        Purpose: Translates each field into its corresponding binary value
        Input: Output dictionary with fields
        Output: Output dictionary with binary values 
        """
        
        # if the command is a C instrction
        if self.output_dict[i]['commandType'] == 'C':

            if ('=' in self.output_dict[i]['instruction']) and (';' in self.output_dict[i]['instruction']):
                self.output_dict[i]['dest'] = self.output_dict[i]['instruction'].split('=')[0]
                self.output_dict[i]['comp'] = self.output_dict[i]['instruction'].split("=")[1]
                self.output_dict[i]['jump'] = self.output_dict[i]['instruction'].split(";")[1]

            if ('=' in self.output_dict[i]['instruction']) and (';' not in self.output_dict[i]['instruction']):
                self.output_dict[i]['dest'] = self.output_dict[i]['instruction'].split('=')[0]
                self.output_dict[i]['comp'] = self.output_dict[i]['instruction'].split("=")[1]
                self.output_dict[i]['jump'] = 'null'

            if ('=' not in self.output_dict[i]['instruction']) and (';' in self.output_dict[i]['instruction']):
                self.output_dict[i]['dest'] = 'null'
                self.output_dict[i]['comp'] = self.output_dict[i]['instruction'].split(";")[0]
                self.output_dict[i]['jump'] = self.output_dict[i]['instruction'].split(";")[1]  
            
            # calculate the binary values of each bit type in “ixxaccccccdddjjj”
            control_bit = '111'
            a_bit = self.translation_dict['a_dict'][self.output_dict[i]['comp']] 
            c_bit = self.translation_dict['comp_dict'][self.output_dict[i]['comp']]
            d_bit = self.translation_dict['dest_dict'][self.output_dict[i]['dest']] 
            j_bit = self.translation_dict['jump_dict'][self.output_dict[i]['jump']]
            self.output_dict[i]['binary_translation'] = control_bit + a_bit + c_bit + d_bit + j_bit
        
        # if the command is an A instrction
        if self.output_dict[i]['commandType'] == 'A':
            self.output_dict[i]['binary_translation'] = '0' + format(int(self.output_dict[i]['symbol']), '015b') 
        
        return
    
    def output_dict_first_symbol_update(self): 
        """
        Purpose: First pass of the symbol table
        Input: Initialised symbol dicitonary
        Output: Symbol dictionary with new non-standard A and C symbols added
        """
        for i in range(len(self.input_data)): self.symbol_dict_first_update(i)
        return
    
    def output_dict_second_symbol_update(self): 
        """
        Purpose: Second pass of the symbol table
        Input: Initialised symbol dicitonary
        Output: Symbol dictionary with new non-standard L symbols added
        """
        for i in range(len(self.input_data)): self.symbol_dict_second_update(i)
        return

    def get_output_dict_symbols(self):  
        """
        Purpose: Add symbols to the output dictionary
        Input: Initialised symbol dicitonary and output dictionary
        Output: Output dictionary updated with symbols
        """
        for i in range(len(self.input_data)): self.get_symbol_value(i)
        return
    
    def get_output_dict_binary(self):  
        """
        Purpose: Add binary to the output dictionary
        Input: Initialised symbol dicitonary and output dictionary
        Output: Output dictionary updated with binary translations
        """
        for i in range(len(self.input_data)): self.get_code(i)
        return 
    
    def write_binary_output(self):  
        """
        Purpose: Write binary translation to output file
        Input: Output dictionary with binary translation fields, specified output file name
        Output: Binary written to output file
        """
        with open(self.output_file, 'w') as log:
            for i in range(len(self.input_data)):
                if self.output_dict[i]['commandType'] == 'A' or self.output_dict[i]['commandType'] == 'C':
                    log.write('{}\n'.format(self.output_dict[i]['binary_translation']))
        return



if __name__ == '__main__':  
    """
    Purpose: Develop a HackAssembler program that translates Hack assembly code
             into executable Hack binary code
    Input: Source programme is supplied in text file called Xxx.asm
    Output: Generated source code is written into a text file called Xxx.asm
    """
     
    # initialising the Assembler class
    HackAssembler = Assembler() # initialise the assembler object
    HackAssembler.input_file = 'pong/Pong.asm' # initialise the input file
    HackAssembler.output_file = 'Pong.hack' # initialise the output file    

    # assemble key data structures
    HackAssembler.parser(HackAssembler.input_file) # reading the input and capturing commands
    HackAssembler.make_translation_dict() # create the Hack to binary translation dictionary
    HackAssembler.make_symbol_dict() # creat the standard symbol dictionary
    HackAssembler.make_output_dict(HackAssembler.input_data) # create the output dictionary
 
    # run the first update on the output dictionary
    HackAssembler.update_output_dict() 
    
    # first pass to update symbol tabe 
    HackAssembler.output_dict_first_symbol_update()
    
    # second pass to update symbol tabe
    HackAssembler.output_dict_second_symbol_update()

    # get symbols into the output dictionary
    HackAssembler.get_output_dict_symbols()
    
    # get binary translations into the output dictionary
    HackAssembler.get_output_dict_binary()

    # write binary translations to file
    HackAssembler.write_binary_output()


    

    