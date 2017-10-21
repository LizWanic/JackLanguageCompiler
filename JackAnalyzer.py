#
#JackAnalyzer.py
#
# CS2002   Project 11 Jack Compiler 
#
# last updated 1 December 2016 by Elizabeth Wanic
#

import sys  #for grading server
from pathlib import *

from JackTokenizer import *
from CompilationEngine import *
from JTConstants import *

class JackAnalyzer(object):

##########################################
#Constructor

    def __init__(self, target):
        
        self.targetPath = Path(target)
        self.crossFileConditionalStatementCounter = 0

##########################################
#public methods
        
    def process(self):
        ''' iterates over a directory causing each .jack file to be processed.
            returns the pathname of the directory upon successful completion. '''
        
        if self.targetPath.is_dir():
            for eachFile in self.targetPath.iterdir():
                if eachFile.suffix == '.jack':
                    self.__processFile__(eachFile)  #file as a pathlib object
                    
        else:
            raise RuntimeError("Error, " + target.name + " is not a directory ")
        
        return str(self.targetPath)


##########################################
#private methods
    
    def __processFile__(self, filePath):
        ''' processes a single file, first feeding the file to JackTokenizer to generate a list of tokens
            (output as T.xml files for debugging use) and that token list is fed through
            CompilationEngine to generate a final result list of XML tokens which is output into an .xml file. '''


        TXML_tokens = []
        tokenizer = JackTokenizer(filePath)
                
        TXML_tokens.append('<tokens>')
        while True:
            nextLine = tokenizer.advance()           
            
            if nextLine:
                TXML_tokens.append(self.__wrapTokenInXML__(nextLine))
                
            else:
                TXML_tokens.append('</tokens>')
                break
            
        #outputs the first list to the 'T.xml' file                   
        self.__output__(str(self.targetPath) + '/' + str(filePath.stem) + 'T.xml', TXML_tokens)
        
        #calls the CompilationEngine on the TXML_tokens 
        compEng = CompilationEngine(TXML_tokens)
        
        #uses the cross file counter for writing the VM code
        compEng.vmWriterCounter = self.crossFileConditionalStatementCounter
        
        XML_tokens = compEng.compileTokens()
        
        #takes the counter from the latest VM file and updates the crossfile counter
        self.crossFileConditionalStatementCounter = compEng.vmWriterCounter
        
        #outputs the list to the '.xml' file 
        self.__output__(str(self.targetPath) + '/' + str(filePath.stem) + '.xml', XML_tokens)
 
        #outputs the '.vm' file
        self.__output__(str(self.targetPath) + '/' + str(filePath.stem) + '.vm', compEng.get_vmInstructions())


    def __output__(self, filePath, codeList):
        ''' outputs the VM code codeList into a file and returns the file path'''
        
        file = open(str(filePath), 'w')
        file.write("\n".join(codeList))
        file.write("\n")
        file.close()


    def __wrapTokenInXML__(self, token):
        ''' returns an XML tag pair with the token properly sandwiched.
             conducts proper substitutions and quotation mark removals. '''
        
        flavor = 'unknown'        
        
        if token in SYMBOLS or token in OPERATORS:
            flavor = 'symbol'
        elif token in KEYWORDS:
            flavor = 'keyword'
        elif token[0] == '"':
            flavor = 'stringConstant'
            token = token[1:-1]
        elif token[0].isdigit():
            flavor = 'integerConstant'
        else:
            flavor = 'identifier'
        
        return '<' + flavor + '> ' + token + ' </' + flavor + '>'



#################################
#################################
#################################
#this kicks off the program and assigns the argument to a variable
#
if __name__=="__main__":

    target = sys.argv[1]     # use this one for final deliverable

    #project 10 tests
##    target = 'ExpressionlessSquare'
##    target = 'ArrayTest'
##    target = 'Square'


    #project 11 tests
##    target = 'Seven'
##    target = 'ConvertToBin'
##    target = 'Square'
##    target = 'Average'
##    target = 'Pong'
##    target = 'ComplexArrays'
    
    analyzer = JackAnalyzer(target)
    print('\n' + analyzer.process() + ' has been translated.')







    
