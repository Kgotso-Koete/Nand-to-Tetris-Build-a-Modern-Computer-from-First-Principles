# Uses python3
import re

class VMtranslator:

    def __init__(self):
        # I/O data structures
        self.input_file = None # input file used to parse commands
        self.output_file = None  # output file where binary code will be written

        # key data structures
        self.input_data = None  # commands parsed and captured in list format
        self.standard_VMcommand_table = None # standard VM commands and their types 
        self.standard_VMtosymbol = None # standard VM memory command to assembly symbol map
        self.output_dict = None # output dictionary that will store the translation
        self.jmp_count = 0
        
    def parser(self, input_file):
        """
        Purpose: Unpacks each underlying instructin into it's underlying fields
        Input:Text file containing instuctions
        Output: Data structure containing fields
        """
        self.input_data = []
        # open file
        with open(input_file, 'r') as f:
            source = [line.rstrip() for line in f]   
            for cmd in source:
                if not cmd.startswith('//') and not cmd == '': 
                    self.input_data.append(cmd.split())
        return 
    
    def initialise_output_dictionary(self, input_data):
        """
        Purpose: Stores the input data into an output dictionary
        Input: List containing instructions
        Output: Dictionary with various fields
        """
        self.output_dict = {}
        for i in range(len(input_data)):
            self.output_dict[i] = input_data[i]
        return
    
    def initialise_standard_VMcommand_table(self):
        """
        Purpose: Stores the standard commands and their types of the VM
        Input: An empty dictionary
        Output: Dictionary with various fields
        """
        self.standard_VMcommand_table = {'add': 'C_ARITHMETIC', 'sub': 'C_ARITHMETIC', 'neg': 'C_ARITHMETIC', 'eq': 'C_ARITHMETIC',
                                         'gt': 'C_ARITHMETIC', 'lt': 'C_ARITHMETIC','and': 'C_ARITHMETIC','or': 'C_ARITHMETIC',
                                         'not': 'C_ARITHMETIC','pop': 'C_POP', 'push': 'C_PUSH'}
         
        return
    
    
    def initialise_standard_VMtosymbol(self):
        """
        Purpose: Set up the standard VM memory command to assembly symbol map
        Input: Uninitialized standard VM to asm symbol map
        Output: Initialized standard VM to asm symbol map
        """
        self.standard_VMtosymbol = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT'}
        return

    def initialise_output_dict(self, input_data):
        """
        Purpose: Initialise the output dictionary
        Input: Uninitialised output dictionary
        Output: Output dictionary initialised with commands 
        """
        self.output_dict = {}
        for i in range(len(input_data)):
            self.output_dict[i] = {}
            self.output_dict[i]['VM code'] = ''
            self.output_dict[i]['VM cmd type'] = '' 
            self.output_dict[i]['assembly code'] = '' 

        return 
    
    def get_VMcode_type(self, input_data):
        """
        Purpose: Load VM commmand types in the output dictionary with each command
        Input: An empty output dictionary
        Output: Output dictionary initialised with commands and their type
        """
        for i in range(len(input_data)):
            self.output_dict[i]['VM code'] = input_data[i]
            VM_cmd = self.output_dict[i]['VM code'][0]
            self.output_dict[i]['VM cmd type'] = self.standard_VMcommand_table[VM_cmd]   

        return
    
    def code_C_PUSH(self, i, VM_code, command):
        """
        Purpose: Converts single 'push' VM commands into assembly code
        Input: Ouptut dictionary containing 'push' VM commands and their type
        Output: Output dictionary updated with 'push' assembly transaltions 
        """

        segment = VM_code[1] # local, constant, argument? etc
        index = VM_code[2] # index to be used in push/pop the value of segment[index] in stack
        assembly = ''    

        if segment in self.standard_VMtosymbol:
            asm_symbol = self.standard_VMtosymbol[segment] 
            # addr = segment_pointer + index, *SP = *addr, SP ++
            add_index = ['@' + index,'D=A'] # load into index into the D register
            addr = ['@' + asm_symbol, 'M=M+D', 'A=M'] # addr = segment_pointer + index 
            data_to_push = ['D=M'] # *addr 
            SP_move = ['@SP', 'A=M', 'M=D'] # *SP = *addr 
            SP_increment = ['@SP','M=M+1'] # SP ++ 
            minus_index = ['@' + index,'D=A'] # load into index into the D register 
            reset_addr = ['@' + asm_symbol, 'M=M-D'] # addr = segment_pointer + index  
            assembly = add_index + addr + data_to_push + SP_move + SP_increment + minus_index + reset_addr
            return assembly 
        
        if  segment == 'constant':
            # addr = constant, *SP = *addr, SP ++
            addr = ['@' + index] # addr = constant
            data_to_push = ['D=A'] # *addr  
            SP_move = ['@SP', 'A=M', 'M=D'] # *SP = *addr 
            SP_increment = ['@SP','M=M+1'] # SP ++ 
            assembly = addr + data_to_push + SP_move + SP_increment
            return assembly  
        
        if  segment == 'temp':
            # addr = segment_pointer + index, *SP = *addr, SP ++
            addr = ['@R' + str(5 + int(index))] # addr = segment_pointer + index   
            data_to_push = ['D=M'] # *addr 
            SP_move = ['@SP', 'A=M', 'M=D'] # *SP = *addr 
            SP_increment = ['@SP','M=M+1'] # SP ++ 
            assembly = addr + data_to_push + SP_move + SP_increment
            return assembly 
        
        if segment == 'pointer' and index == '0':  
            # *SP = THIS/THAT,SP++
            data_to_push = ['@THIS','D=M'] # THIS    
            SP_val = ['@SP', 'A=M', 'M=D'] # *SP 
            SP_increment = ['@SP','M=M+1'] # SP ++ 
            assembly = data_to_push + SP_val + SP_increment
            return assembly
        
        if segment == 'pointer' and index == '1': 
            # *SP = THIS/THAT,SP++
            data_to_push = ['@THAT','D=M'] # THAT      
            SP_val = ['@SP', 'A=M', 'M=D'] # *SP 
            SP_increment = ['@SP','M=M+1'] # SP ++ 
            assembly = data_to_push + SP_val + SP_increment 
            return assembly
        
        if segment == 'static':  
            data_to_push = ['@Foo.' + index, 'D=M'] 
            SP_val = ['@SP', 'A=M', 'M=D'] # *SP 
            SP_increment = ['@SP','M=M+1'] # SP ++ 
            assembly = data_to_push + SP_val + SP_increment 
            return assembly
 
        return
    
    def code_C_POP(self, i, VM_code, command):
        """
        Purpose: Converts single 'pop' VM commands into assembly code
        Input: Ouptut dictionary containing 'pop' VM commands and their type
        Output: Output dictionary updated with 'pop' assembly transaltions 
        """

        segment = VM_code[1] # local, constant, argument? etc
        index = VM_code[2] # index to be used in push/pop the value of segment[index] in stack
        assembly = ''

        if segment in self.standard_VMtosymbol:
            asm_symbol = self.standard_VMtosymbol[segment] 
            # addr = segment_pointer + index, SP--, *addr = *SP
            add_index = ['@' + index,'D=A'] # load into index into the D register 
            addr = ['@' + asm_symbol, 'M=M+D'] # addr = segment_pointer + index 
            SP_decrement = ['@SP','M=M-1','A=M'] # SP -- 
            data_to_push = ['D=M'] # *SP 
            segment_change = ['@' + asm_symbol,'A=M', 'M=D'] # *addr = *SP 
            minus_index = ['@' + index,'D=A'] # load into index into the D register 
            reset_addr = ['@' + asm_symbol, 'M=M-D'] # addr = segment_pointer + index  
            reset_pointer_memory = ['@SP','A=M','M=0']  
            assembly = add_index + addr + SP_decrement + data_to_push + segment_change + minus_index + reset_addr + reset_pointer_memory
            return assembly    
        
        if segment == 'temp':
            # addr = segment_pointer + index, SP--, *addr = *SP 
            SP_decrement = ['@SP','M=M-1','A=M'] # SP -- 
            data_to_push = ['D=M'] # *SP 
            segment_change = ['@R' + str(5 + int(index)), 'M=D'] # *addr = *SP 
            reset_pointer_memory = ['@SP','A=M','M=0']
            assembly = SP_decrement + data_to_push + segment_change + reset_pointer_memory
            return assembly  
        
        if segment == 'pointer' and index == '0':  
            # *SP--,THIS/THAT = *SP
            SP_decrement = ['@SP','M=M-1','A=M'] # SP -- 
            data_to_push = ['D=M'] # *SP
            segment_change = ['@THIS', 'M=D'] # THIS/THAT = *SP
            reset_pointer_memory = ['@SP','A=M','M=0']  
            assembly = SP_decrement + data_to_push + segment_change + reset_pointer_memory
            return assembly
        
        if segment == 'pointer' and index == '1':  
            # *SP--,THIS/THAT = *SP
            SP_decrement = ['@SP','M=M-1','A=M'] # SP -- 
            data_to_push = ['D=M'] # *SP
            segment_change = ['@THAT', 'M=D'] # THIS/THAT = *SP
            reset_pointer_memory = ['@SP','A=M','M=0']           
            assembly = SP_decrement + data_to_push + segment_change + reset_pointer_memory
            return assembly
        
        if segment == 'static':
            SP_decrement = ['@SP','M=M-1','A=M'] # SP -- 
            data_to_push = ['D=M'] # *SP
            segment_change = ['@Foo.' + index, 'M=D'] # THIS/THAT = *SP
            reset_pointer_memory = ['@SP','A=M','M=0']            
            assembly = SP_decrement + data_to_push + segment_change + reset_pointer_memory
            return assembly
 

        return
    
    def code_C_ARITHMETIC(self, i, VM_code, command):
        """
        Purpose: Converts single 'arithmetic' VM commands into assembly code
        Input: Ouptut dictionary containing 'arithmetic'' VM commands and their type
        Output: Output dictionary updated with 'arithmetic'' assembly transaltions 
        """

        arithmetic_command = VM_code[0] # add, subtract? etc
        assembly = ''
        

        if arithmetic_command == 'add':
            # SP --, pop *SP, SP--, pop 
            SP_decrement_1 = ['@SP','M=M-1'] # SP--
            n_1 = ['A=M','D=M'] # n1 = pop
            reset_pointer_memory1 = ['@SP','A=M','M=0']
            SP_decrement_2 = ['@SP','M=M-1'] # SP--
            n_2 = ['A=M','D=D+M'] # n2 = pop
            to_push = ['@SP', 'A=M','M=D','@SP','M=M+1']     
            assembly = SP_decrement_1 + n_1 + reset_pointer_memory1 + SP_decrement_2 + n_2 + to_push 
            return assembly 
        
        if arithmetic_command == 'sub':
             # SP --, pop *SP, SP--, pop 
            SP_decrement_1 = ['@SP','M=M-1'] # SP--
            n_1 = ['A=M','D=M'] # n1 = pop 
            neg = ['@0', 'D=A-D'] # TO DELETE ADFTER TESTING 
            reset_pointer_memory1 = ['@SP','A=M','M=0']
            SP_decrement_2 = ['@SP','M=M-1'] # SP--
            n_2 = ['A=M','D=D+M'] # n2 = pop      
            to_push = ['@SP', 'A=M','M=D','@SP','M=M+1']     
            assembly = SP_decrement_1 + n_1 + neg + reset_pointer_memory1 + SP_decrement_2 + n_2 + to_push
            return assembly
        
        if arithmetic_command == 'neg':
            SP_decrement = ['@SP','M=M-1'] # SP--
            n = ['A=M','D=M'] # n1 = pop 
            neg = ['@0', 'D=A-D'] # TO DELETE ADFTER TESTING
            change = ['@SP','A=M', 'M=D']  
            SP_increment = ['@SP','M=M+1'] # SP ++
            assembly = SP_decrement + n + neg + change + SP_increment
            return assembly 
        
        if arithmetic_command == 'eq': 
            self.jmp_count += 1
            SP_decrement_1 = ['@SP','M=M-1'] # SP--
            n_1 = ['A=M','D=M'] # n1 = pop 
            reset_pointer_memory1 = ['@SP','A=M','M=0']
            SP_decrement_2 = ['@SP','M=M-1'] # SP--
            n_2 = ['A=M','D=D-M'] # n2 = pop 
            jmp_cond = ['@TRUE_COND' + str(self.jmp_count),'D;JEQ']       
            false_cond = ['@SP','A=M', 'M=0']   
            SP_increment1 = ['@SP','M=M+1'] # SP ++   
            skip1 = ['D=0', '@SKIP' + str(self.jmp_count), 'D;JEQ']  
            true_cond = ['(TRUE_COND' + str(self.jmp_count) + ')','@SP', 'A=M', 'M=-1'] 
            SP_increment2 = ['@SP','M=M+1'] # SP ++  
            skip2 = ['(SKIP'+ str(self.jmp_count) + ')']        
            assembly = SP_decrement_1 + n_1 + reset_pointer_memory1 + SP_decrement_2 + n_2 + jmp_cond + false_cond + SP_increment1 + skip1 + true_cond + SP_increment2 + skip2
            return assembly
        
        if arithmetic_command == 'gt':
            self.jmp_count += 1
            SP_decrement_1 = ['@SP','M=M-1'] # SP--
            n_1 = ['A=M','D=M'] # n1 = pop 
            reset_pointer_memory1 = ['@SP','A=M','M=0']
            SP_decrement_2 = ['@SP','M=M-1'] # SP--
            n_2 = ['A=M','D=D-M'] # n2 = pop 
            jmp_cond = ['@TRUE_COND' + str(self.jmp_count),'D;JLT']       
            false_cond = ['@SP','A=M', 'M=0']   
            SP_increment1 = ['@SP','M=M+1'] # SP ++   
            skip1 = ['D=0', '@SKIP' + str(self.jmp_count), 'D;JEQ']  
            true_cond = ['(TRUE_COND' + str(self.jmp_count) + ')','@SP', 'A=M', 'M=-1'] 
            SP_increment2 = ['@SP','M=M+1'] # SP ++  
            skip2 = ['(SKIP'+ str(self.jmp_count) + ')']        
            assembly = SP_decrement_1 + n_1 + reset_pointer_memory1 + SP_decrement_2 + n_2 + jmp_cond + false_cond + SP_increment1 + skip1 + true_cond + SP_increment2 + skip2
            return assembly       

        if arithmetic_command == 'lt':
            self.jmp_count += 1
            SP_decrement_1 = ['@SP','M=M-1'] # SP--
            n_1 = ['A=M','D=M'] # n1 = pop 
            reset_pointer_memory1 = ['@SP','A=M','M=0']
            SP_decrement_2 = ['@SP','M=M-1'] # SP--
            n_2 = ['A=M','D=D-M'] # n2 = pop 
            jmp_cond = ['@TRUE_COND' + str(self.jmp_count),'D;JGT']        
            false_cond = ['@SP','A=M', 'M=0']   
            SP_increment1 = ['@SP','M=M+1'] # SP ++   
            skip1 = ['D=0', '@SKIP' + str(self.jmp_count), 'D;JEQ']  
            true_cond = ['(TRUE_COND' + str(self.jmp_count) + ')','@SP', 'A=M', 'M=-1'] 
            SP_increment2 = ['@SP','M=M+1'] # SP ++  
            skip2 = ['(SKIP'+ str(self.jmp_count) + ')']        
            assembly = SP_decrement_1 + n_1 + reset_pointer_memory1 + SP_decrement_2 + n_2 + jmp_cond + false_cond + SP_increment1 + skip1 + true_cond + SP_increment2 + skip2
            return assembly    
        
        if arithmetic_command == 'and':
            SP_decrement_1 = ['@SP','M=M-1'] # SP--
            n_1 = ['A=M','D=M'] # n1 = pop 
            reset_pointer_memory1 = ['@SP','A=M','M=0'] 
            SP_decrement_2 = ['@SP','M=M-1'] # SP--
            n_2 = ['A=M','D=D&M'] # n2 = pop
            change = ['@SP','A=M', 'M=D']   
            SP_increment = ['@SP','M=M+1'] # SP ++
            assembly = SP_decrement_1 + n_1 + reset_pointer_memory1 + SP_decrement_2 + n_2 + change + SP_increment
            return assembly 

        if arithmetic_command == 'or':
            SP_decrement_1 = ['@SP','M=M-1'] # SP--
            n_1 = ['A=M','D=M'] # n1 = pop 
            reset_pointer_memory1 = ['@SP','A=M','M=0']
            SP_decrement_2 = ['@SP','M=M-1'] # SP--
            n_2 = ['A=M','D=D|M'] # n2 = pop  
            change = ['@SP','A=M', 'M=D']  
            SP_increment = ['@SP','M=M+1'] # SP ++ 
            assembly = SP_decrement_1 + n_1 + reset_pointer_memory1 + SP_decrement_2 + n_2 + change + SP_increment
            return assembly  
           
        if arithmetic_command == 'not':
            SP_decrement = ['@SP','M=M-1'] # SP--
            n = ['A=M','D=M'] # n1 = pop 
            neg = ['@0', 'D=!D'] # TO DELETE ADFTER TESTING
            change = ['@SP','A=M', 'M=D']  
            SP_increment = ['@SP','M=M+1'] # SP ++ 
            assembly = SP_decrement + n + neg + change + SP_increment  
            return assembly   
                   
   
        return 
        
    def code_writer(self, i):
        """
        Purpose: Converts single VM commands into assembly code
        Input: Ouptut dictionary containing VM commands and their type
        Output: Output dictionary updated with assembly transaltions
        """
        
        VM_code = self.output_dict[i]['VM code'] # entire VM code command
        command = self.output_dict[i]['VM cmd type'] # C-PUSH, C_POP or C_ARITHMETIC etc?
        
        if command == 'C_PUSH': return self.code_C_PUSH(i, VM_code, command) # PUSH?
        if command == 'C_POP': return self.code_C_POP(i, VM_code, command) # POP?
        if command == 'C_ARITHMETIC': return self.code_C_ARITHMETIC(i, VM_code, command) # C_ARITHMETIC? 
        
        return 
    
    def translate(self):
        """
        Purpose: Converts all VM commands into assembly code
        Input: Ouptut dictionary containing VM commands and their type
        Output: Output dictionary updated with assembly transaltions
        """

        for i in range(len(self.input_data)):
            self.output_dict[i]['assembly code'] = self.code_writer(i) 
        
        return


    def write_asm_output(self):  
        """
        Purpose: Write asm translation to output file
        Input: Output dictionary with asm translation fields, specified output file name
        Output: Asm written to prog.asm output file
        """
        with open(self.output_file, 'w') as log: 
            for i in range(len(self.input_data)): 
                for j in range (len(self.output_dict[i]['assembly code'])):
                    log.write('{}\n'.format(self.output_dict[i]['assembly code'][j]))    
        return


if __name__ == '__main__':  
    """
    Purpose: Develop a VM translater program that translates VM code into executable Hack code
    Input: Source programme is supplied in text file called prog.vm
    Output: Generated source code is written into a text file called prog.asm
    """
    import sys
    
    # initialising the Assembler class and I/O files
    VMtranslator = VMtranslator() # initialise the assembler object
    VMtranslator.input_file = sys.argv[1] # initialise the input file
    VMtranslator.output_file = sys.argv[1][:-3] + '.asm' # initialise the output file   
      
    # initialise key data structures   
    VMtranslator.parser(VMtranslator.input_file) # load all commands into the input data list
    VMtranslator.initialise_output_dictionary(VMtranslator.input_data) # load the commands into an output dictionary
    VMtranslator.initialise_standard_VMcommand_table() # load standard VM commands and their types
    VMtranslator.initialise_standard_VMtosymbol() # set up the standard VM memory command to assembly symbol map
    VMtranslator.initialise_output_dict(VMtranslator.input_data) # initialise the output dictionary

    # begin pre-translation processing 
    VMtranslator.get_VMcode_type(VMtranslator.input_data)# Load VM commmand types in the output dictionary with each command

    # begin translating 
    VMtranslator.translate()  
    VMtranslator.write_asm_output()    
       
    #for k,v in VMtranslator.output_dict.items(): print(v)  
    
        
 
    


    

     