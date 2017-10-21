#
#JackTokenizer.py
#
# CS2002   Project 10 Jack Compiler (part 1)
#
# last updated 4 November 2016 by Elizabeth Wanic
# 
# No updates for Project 11


from JTConstants import *

   
############################################
# Class
class JackTokenizer(object):

############################################
# Constructor

    def __init__(self, filePath):
        loadedList = self.__loadFile__(str(filePath))
        
        self.toParse = self.__filterFile__(loadedList)


# ############################################
# instance methods

    def advance(self):
        '''reads and returns the next token, returns None if there are no more tokens.'''

        if self.toParse:

            self.toParse[0] = self.toParse[0].strip()
            line = self.toParse[0]
            token = self.__parseInt__(line) + self.__parseCharacters__(line) + self.__parseString__(line)
            
            #if needed to change from simple symbol to glyphSubstitutes value set length to 1
            if token in glyphSubstitutes.values():
                length = 1
                if length < len(self.toParse[0]):
                    self.toParse[0] = line[length:]     
                else:
                    self.toParse.pop(0)                
            
            #otherwise remove characters up to the length of the token       
            else:
                length = len(token)
                if length < len(self.toParse[0]):
                    self.toParse[0] = line[length:]
            
                else:
                    self.toParse.pop(0)            

            return token            

        else:
            return None



#############################################
# private


    def __parseInt__(self, line):
        ''' returns an integerConstant off of the start of the line.
            assumes there are no leading spaces
            does not modify the line itself. '''

        number = ""
        
        i = 0 
        
        while line[i].isdigit():
            number += line[i]
            i += 1
            
        return number
        
        
    def __parseCharacters__(self, line):
        ''' returns a token off of the start of the line which could be an identifier or a keyword.
            assumes there are no leading spaces
            does not modify the line itself. '''
        
        chars = ""
                
        if line[0] in SYMBOLS:
            
            chars = line[0]
            
            if line[0] in glyphSubstitutes:
                chars = glyphSubstitutes[line[0]]
            
        else:
            i = 0 
        
            while line[i].isalpha():
                chars += line[i]
                i += 1
                    
        return chars       


    def __parseString__(self, line):
        ''' returns a stringConstant off of the start of the line, quotes left in place.
            assumes there are no leading spaces and that the leading double quote has not been stripped.
            does not modify the line itself. '''
        
        string = ""
         
        if line[0] == '"':
            string += line[0]
        
            i = 1
                
            while line[i] != '"':
                string += line[i]
                i += 1
                
            string += '"'
        
        return string

    ############   file loading stuff below   ############   

    def __loadFile__(self, fileName):
        '''Loads the file into memory.

           -fileName is a String representation of a file name,
           returns contents as a simple List'''
        
        fileList = []
        file = open(fileName,"r")
        
        for line in file:
            fileList.append(line)
            
        file.close()
        
        return fileList



    def __filterFile__(self, fileList):
        '''Comments, blank lines and unnecessary leading/trailing whitespace are removed from the list.

           -fileList is a List representation of a file, one line per element
           returns the fully filtered List'''

        filteredList = []
                
        for line in fileList:
            line = line.strip()                                             #removes leading and trailing whitespace removal
            line = self.__filterOutEOLComments__(line)                      #calls self.__filterOutEOLComments_()
            
            if len(line) > 0:
                line = self.__filterOutSingleLineBlockComments__(line)      #check for and remove singleLineBlockComments
                    
                if len(line) > 0:                                           #if not an empty line, append it to the filtered list
                    filteredList.append(line)
                
        return filteredList   
        
        
    def __filterOutEOLComments__(self, line):
        '''Removes end-of-line comments and and resulting whitespace.

           -line is a string representing single line, line endings already stripped
           returns the filtered line, which may be empty '''

        index = line.find('//')                     #look for the '//' indicator and remove comments from that point
        if index >= 0:
            line = line[0:index]

        line = line.strip()

        return line     


    def __filterOutSingleLineBlockComments__(self, line):
        '''Removes single line block comments and resulting whitespace.
           There may valid code following a single line block comment so entire lines are not deleted.

           -line is a string representing single line, line endings already stripped
           returns the filtered line, which may be empty. '''

        lineOut = ''
        
        if line[0] == "/" and line[1] == "*":                   #finds beginning of block comment
            if len(line) > 3:
                for i in range(3,len(line)):                    #goes through comment until '*/' is encountered
                    if line[i] == "*" and line[i+1] == "/":
                        lineOut += (line[i+2:])
            return lineOut
            
        elif line[0] == "*":                                    #removes the interior lines of the block comment
            return lineOut
        
        else:
            lineOut = line
            return lineOut
            
            



