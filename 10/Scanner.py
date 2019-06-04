from Character import Character  
import re
 
class Scanner:  
 
    """ A Scanner object reads through the sourceText and returns one character at a time or tokenized text"""

    def __init__(self, source_text_path):
        self.source_text_path = source_text_path
        self.original_source_text = ""
        self.modified_source_text = ""
        self.EOF_index = None
        self.endmark = "\0"  
        self.word_list = None 

        # save all the source text in a string  
        with open(self.source_text_path, 'r') as file: self.original_source_text = file.read()
        self.EOF_index = len(self.original_source_text) - 1
    
    def file_read(self):
        """ Stores instruction code into text without white spaces or comments"""
        with open(self.source_text_path, 'r') as myfile:
            data = myfile.read() 
        comments = re.compile(r'''
            (//[^\n]*(?:\n|$))    # Everything between // and the end of the line/file
            |                     # or 
            (/\*.*?\*/)           # Everything between /* and */
            |
            \/\*[\s\S]*?\*\/|([^:]|^)\/\/.*$ # Every comment between /** and */  
            ''', re.VERBOSE)
        self.modified_source_text = comments.sub('\n', data)  
        return self.modified_source_text 
  