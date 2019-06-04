# Uses python3
import re

def is_number(n):
    try:
        float(n)   # Type-casting the string to `float`.
                   # If string is not a valid `float`, 
                   # it'll raise `ValueError` exception
    except ValueError:
        return False
    return True

def parser(source_file):
    """
    Purpose: Unpacks each underlying instructin into it's underlying fields
    Input:Text file containing instuctions
    Output: Data structure containing fields
    """
    # source: https://stackoverflow.com/a/52732203/6556133
    source_re = r'(?m)^ *(.*?) *(?:/.*)?$'  # Regex each line from file without line breaks 
    # open file
    with open(source_file, 'r') as infile:
        source = infile.read().strip()
        match = re.sub(source_re , r'\1', source)
    # put data in a list
    data = match.split()
    return data  

def get_code(command_dict, i):
    """
    Purpose: Translates each field into its corresponding binary value
    Input: Dictionary with fields
    Output: Dictionary with binary values
    """
    # translation dictionary for a-bit of “ixxaccccccdddjjj”
    a_dict =     {'0':'0',
                  '1':'0',
                  '-1':'0',
                  'D':'0',
                  'A':'0',
                  '!D':'0',
                  '!A':'0',
                  '-D':'0',
                  '-A':'0',
                  'D+1':'0',
                  'A+1':'0',
                  'D-1':'0',
                  'A-1':'0',
                  'D+A':'0',
                  'D-A':'0',
                  'A-D':'0',
                  'D&A':'0',
                  'D|A':'0',
                  'M':'1',
                  '!M':'1',
                  '-M':'1',
                  'M+1':'1',
                  'M-1':'1',
                  'D+M':'1',
                  'D-M':'1',
                  'M-D':'1',
                  'D&M':'1',
                  'D|M':'1'
                }
    
    # translation dictionary for c1 to c6-bit of “ixxaccccccdddjjj”
    comp_dict = {'0':'101010',
                  '1':'111111',
                  '-1':'111010',
                  'D':'001100',
                  'A':'110000',
                  '!D':'001101',
                  '!A':'110001',
                  '-D':'001111',
                  '-A':'110011',
                  'D+1':'011111',
                  'A+1':'110111',
                  'D-1':'001110',
                  'A-1':'110010',
                  'D+A':'000010',
                  'D-A':'010011',
                  'A-D':'000111',
                  'D&A':'000000',
                  'D|A':'010101',
                  'M':'110000',
                  '!M':'110001',
                  '-M':'110011',
                  'M+1':'110111',
                  'M-1':'110010',
                  'D+M':'000010',
                  'D-M':'010011',
                  'M-D':'000111',
                  'D&M':'000000',
                  'D|M':'010101'
                 }
    
    # translation dictionary for destination-bits (d1,d2,d3) of “ixxaccccccdddjjj”
    dest_dict = {'null':'000',
                  'M':'001',
                  'D':'010',
                  'MD':'011',
                  'A':'100',
                  'AM':'101',
                  'AD':'110',
                  'AMD':'111'
                 }
    
    # translation dictionary for destination-bits (d1,d2,d3) of “ixxaccccccdddjjj”
    jump_dict = {'null':'000',
                  'JGT':'001',
                  'JEQ':'010',
                  'JGE':'011',
                  'JLT':'100',
                  'JNE':'101',
                  'JLE':'110',
                  'JMP':'111'
                 }

    # if the command is a C instrction
    if command_dict[i]['commandType'] == 'C':

        if ('=' in command_dict[i]['instruction']) and (';' in command_dict[i]['instruction']):
            command_dict[i]['dest'] = command_dict[i]['instruction'].split('=')[0]
            command_dict[i]['comp'] = command_dict[i]['instruction'].split("=")[1]
            command_dict[i]['jump'] = command_dict[i]['instruction'].split(";")[1]

        if ('=' in command_dict[i]['instruction']) and (';' not in command_dict[i]['instruction']):
            command_dict[i]['dest'] = command_dict[i]['instruction'].split('=')[0]
            command_dict[i]['comp'] = command_dict[i]['instruction'].split("=")[1]
            command_dict[i]['jump'] = 'null'

        if ('=' not in command_dict[i]['instruction']) and (';' in command_dict[i]['instruction']):
            command_dict[i]['dest'] = 'null'
            command_dict[i]['comp'] = command_dict[i]['instruction'].split(";")[0]
            command_dict[i]['jump'] = command_dict[i]['instruction'].split(";")[1] 
        
        # calculate the binary values of each bit type in “ixxaccccccdddjjj”
        control_bit = '111'
        a_bit = a_dict[command_dict[i]['comp']] 
        c_bit = comp_dict[command_dict[i]['comp']]
        d_bit = dest_dict[command_dict[i]['dest']] 
        j_bit = jump_dict[command_dict[i]['jump']]
        command_dict[i]['binary_translation'] = control_bit + a_bit + c_bit + d_bit + j_bit
    
    # if the command is an A instrction
    if command_dict[i]['commandType'] == 'A':
        command_dict[i]['binary_translation'] = '0' + format(int(command_dict[i]['symbol']), '015b') 
    
    return

def get_instruction_number(command_dict, i, non_L_position):
    """
    Purpose: Updates each instruction with the appropriate instruction number
    Input: Command list and index of current instruction
    Output: Updated command list with instruction numbers for each instruction
    """
    # add instruction numbers 
    
    if command_dict[i]['commandType'] == 'C': command_dict[i]['instruction_pointer'] = i
    if command_dict[i]['commandType'] == 'A': command_dict[i]['instruction_pointer'] = i
    if command_dict[i]['commandType'] == 'L': command_dict[i]['instruction_pointer'] = non_L_position  + 1

    return

def construct_symbol_table(symbol_dict, command_dict, i):
    """
    Purpose: Collects symbols in a table containing addresses
    Input:Symbol dictionary and command list
    Output: Symbol dictionary and command list that includes symbol addresses
    """
    
    #creating the standard symbol table
    # symbol_dict = {}
    symbol_dict['SP'] = 0
    symbol_dict['LCL'] = 1
    symbol_dict['ARG'] = 2
    symbol_dict['THIS'] = 3
    symbol_dict['THAT'] = 4
    symbol_dict['R0'] = 0 
    symbol_dict['R1'] = 1
    symbol_dict['R2'] = 2
    symbol_dict['R3'] = 3
    symbol_dict['R4'] = 4
    symbol_dict['R5'] = 5
    symbol_dict['R6'] = 6
    symbol_dict['R7'] = 7
    symbol_dict['R8'] = 8
    symbol_dict['R9'] = 9
    symbol_dict['R10'] = 10
    symbol_dict['R11'] = 11
    symbol_dict['R12'] = 12
    symbol_dict['R13'] = 13
    symbol_dict['R14'] = 14
    symbol_dict['R15'] = 15
    symbol_dict['SCREEN'] = 16384
    symbol_dict['KBD'] = 24576

    # update the symbol tables
    if command_dict[i]['commandType'] == 'L':
        if command_dict[i]['instruction'][1:-1] not in symbol_dict:
            symbol_dict[command_dict[i]['instruction'][1:-1]] = command_dict[i]['instruction_pointer']

    return

def update_symbol_table(symbol_dict, command_dict, i, assigned_register):
    """
    Purpose: Collects symbols in a table containing addresses
    Input:Symbol dictionary and command list
    Output: Symbol dictionary and command list that includes symbol addresses
    """
    if command_dict[i]['commandType'] == 'A':
        if not is_number(command_dict[i]['instruction'].split("@")[1]):
            if command_dict[i]['instruction'].split("@")[1] not in symbol_dict:
                symbol_dict[command_dict[i]['instruction'].split("@")[1]] =  assigned_register + 1
                assigned_register += 1  

    return assigned_register

def get_symbol_value(data, symbol_dict, command_dict, i):
    """
    Purpose: Collects symbols in a table containing addresses
    Input:Symbol dictionary and command list
    Output: Symbol dictionary and command list that includes symbol addresses
    """
    
    # update the symbols values
    if command_dict[i]['commandType'] == 'A':
        # if the A instruction is a decimal number
        if is_number(command_dict[i]['instruction'].split("@")[1]):
            command_dict[i]['symbol'] = command_dict[i]['instruction'].split("@")[1]
        
        # if A instruction is not a decimal, then just make the decimal the symbol
        if not is_number(command_dict[i]['instruction'].split("@")[1]):
            temp = '(' +  command_dict[i]['instruction'].split("@")[1] + ')'
            if temp not in data:
                command_dict[i]['symbol'] = symbol_dict[command_dict[i]['instruction'].split("@")[1]]  
            if temp in data:
                command_dict[i]['symbol'] = symbol_dict[command_dict[i]['instruction'].split("@")[1]] - 1
           
    # if the instruction is a symbol
    if command_dict[i]['commandType'] == 'L':  
        if command_dict[i]['instruction'][1:-1] in symbol_dict:
            command_dict[i]['symbol'] = symbol_dict[command_dict[i]['instruction'][1:-1]] 

    return


def command_type(t): 
    """
    Purpose: Determines if the instruction is an A, C or L command
    Input:One line string with instuction
    Output: Command classification
    """
    command = '' 
    if t.startswith('@'):
        command = 'A' # for @Xxx where Xxx is either a symbol or a decimal number 
    elif t.startswith('('):
        command = 'L' # pseudo-command for (Xxx) where Xxx is a symbol.
    else:
        command = 'C' # for dest=comp;jump
    return command


if __name__ == '__main__':  
    """
    Purpose: Develop a HackAssembler program that translates Hack assembly code
             into executable Hack binary code
    Input: Source programme is supplied in text file called Xxx.asm
    Output: Generated source code is written into a text file called Xxx.asm
    """

    # get data from program.asm file
    source_file = 'max/Max.asm'       
    data = parser(source_file)
    command_dict = {}
    symbol_dict = {}
    non_L_position = 0
    assigned_register = 15

    # initialise dictionary
    for i in range(len(data)):
        command_dict[i] = {}
        command_dict[i]['instruction'] = ''
        command_dict[i]['commandType'] = ''  # the type of the current command 
        command_dict[i]['symbol'] = '' # returns the symbol or decimal
        command_dict[i]['a-bit'] = ''
        command_dict[i]['dest'] = '' # returns the dest mnemonic in the current C-command for dest=comp;jump
        command_dict[i]['comp'] = '' # returns the comp mnemonic in the current C-command for dest=comp;jump
        command_dict[i]['jump'] = '' # returns the jump mnemonic in the current C-command for dest=comp;jump
        command_dict[i]['instruction_pointer'] = None
        command_dict[i]['binary_translation'] = ''
    
    # process translation
    for i in range(len(data)):
        # get instructions
        command_dict[i]['instruction'] = data[i]
        # get command types
        command_dict[i]['commandType'] = command_type(data[i])  # the type of the current command 
        # get instruction numbers
        if command_dict[i]['commandType'] == 'A' or command_dict[i]['commandType'] == 'C':
            non_L_position += 1
        get_instruction_number(command_dict, i, non_L_position)
        # construct the symbol table, first pass
        construct_symbol_table(symbol_dict, command_dict, i)
    
    # second pass to update symbol table
    for j in range(len(data)):
        assigned_register = update_symbol_table(symbol_dict, command_dict, j, assigned_register)

    # get symbol values and binary code
    for k in range(len(data)):
        get_symbol_value(data, symbol_dict, command_dict, k)
        get_code(command_dict, k) 
     
    # write binary to .hack and .txt files
    with open('Max.hack','w') as log:
        for i in range(len(data)):
            if command_dict[i]['commandType'] == 'A' or command_dict[i]['commandType'] == 'C':
                log.write('{}\n'.format(command_dict[i]['binary_translation']))
              
     
    