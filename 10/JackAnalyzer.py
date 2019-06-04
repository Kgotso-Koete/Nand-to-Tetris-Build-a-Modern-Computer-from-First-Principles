from Scanner import *
from Lexer import *
from Parser import *

def parser_driver():
    import sys
    import os  

    # initialising the Tockenizer class and I/O files
    JackParser = Parser() # initialise the tokenizer object
    JackParser.cmd_path = sys.argv[1] # save path provided
    JackParser.IS_directory = os.path.isdir(JackParser.cmd_path) # is this a file or a directory

    #-------------------------------------------------------------------
    # Procedure for single files
    #-------------------------------------------------------------------
    if not JackParser.IS_directory:  
        # initialising the Assembler class and I/O files 
        JackParser.input_file_path = sys.argv[1] # initialise the input file
        JackParser.output_file_path = sys.argv[1][:-5] + '.xml'  
        JackParser.current_file_read = JackParser.input_file_path.split('/')[-1]
        #print("Input file path: ", JackParser.input_file_path)
        #print("Output file path: ", JackParser.output_file_path)
        #print("Current file read: ", JackParser.current_file_read) 
        #print( )   
        #print("...")  
 
        # tokenize 
        JackParser.get_token_list()
        
        # Compile into xml
        JackParser.create_xml()
        JackParser.write_xml()
        

     
    #-------------------------------------------------------------------
    # Procedure for directories
    #-------------------------------------------------------------------
    if JackParser.IS_directory:
        for file_name in sorted(os.listdir(JackParser.cmd_path)):
            if file_name.endswith(".jack"):

                # initialising the Assembler class and I/O files 
                JackParser.input_file_path = JackParser.cmd_path + '/' + file_name
                JackParser.output_file_path = JackParser.cmd_path + '/' + file_name[0:-5] + '.xml'
                JackParser.current_file_read = JackParser.input_file_path.split('/')[-1]
                #print("Input file path: ", JackParser.input_file_path)
                #print("Output file path: ", JackParser.output_file_path)
                #print("Current file read: ", JackParser.current_file_read)
                #print()   
                #print("...")   
 
                # tokenize     
                JackParser.get_token_list()  
            
                # Compile and save xml into a list - to be written after loop
                JackParser.create_xml() 
        # write each file into xml         
        JackParser.write_xml()
        

    return     
        
        
  
def main():
    parser_driver()

if __name__ == '__main__':
    main() 