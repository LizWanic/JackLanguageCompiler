#
#CompilationEngine.py
#
# CS2002   Project 11 Jack Compiler (part 2)
#
# 
# last updated 1 December 2016 by Elizabeth Wanic
# 
#

from JTConstants import *
from SymbolTable import *
from VMWriter import *

TT_TOKEN = 0
TT_XML = 1

class CompilationEngine(object):

############################################
# Constructor
    def __init__(self, tokenList):
        self.tokens = tokenList     #the list of tagged tokens to process (a copy was previously output as ____T.xml )
                  
        self.indentation = 0        #add and delete from this for left alignment for XML file readability
        
        self.st = SymbolTable()
        
        self.vmW = VMWriter(self.st)
        self.vmWriterCounter = 0      
        
        #flags for producing .vm code
        self.doCalled = False
        self.inMethod = False
        self.isConstructor = False
        self.voidFlag = False
        self.wasInDo = False
        self.dealingWithClassMethod = False     
        self.dealingWithExternalLibClassMethod = False     
        self.wasDealingWithClassMethod = False     
        self.isFunction = False            
        
############################################
# instance methods

    def compileTokens(self):
        ''' primary call to do the final compilation.
            returns a list of properly identified structured XML with appropriate indentation.'''
        
        self.vmW.setLabelCounter(self.vmWriterCounter)
        
        result = []
        
        tokenTuple = self.__getNextEntry__()        

        if tokenTuple[TT_XML] == '<tokens>':
            result.extend( self.__compileClass__() )
            
            tokenTuple = self.__getNextEntry__()
            if tokenTuple[TT_XML] != '</tokens>':
                raise RuntimeError('Error, this file was not properly tokenized, missing </tokens>')
                
        else:
            raise RuntimeError('Error, this file was not properly tokenized, missing <tokens>')
        
        
        #update the counter for labels
        self.vmWriterCounter = self.vmW.labelCounter   
        
        return result
    
    def get_vmInstructions(self):
        '''returns a fully translated list of VM instructions'''
        return self.vmW.get_VMCodeList()
    


############################################
# private/utility methods


    def __getNextEntry__(self):
        ''' removes and returns the next token from the list of tokens as a tuple of the form
            (token, <tag> token </tag>).
            TT_TOKEN and TT_XML should be used for accessing the tuple components '''
        
        nextLine = self.tokens.pop(0)
        splitToken = nextLine.split()
        
        if nextLine == '<tokens>' or nextLine == '</tokens>':
            tupleToken = (splitToken[TT_TOKEN], nextLine)
        
        else:
            tupleToken = (splitToken[TT_XML], nextLine)
        
        return tupleToken

    def __peekAtNextEntry__(self):
        ''' copies, but does not remove the next token from the list of tokens as a tuple of the form
            (token, <tag> token </tag>).
            TT_TOKEN and TT_XML should be used for accessing the tuple components ''' 

        nextLine = self.tokens[0]
        splitToken = nextLine.split()   
        tupleToken = (splitToken[TT_XML], nextLine)
                
        return tupleToken       


    def __replaceEntry__(self, entry):
        ''' returns a token to the head of the list.
            entry must properly be in the form (token, <tag> token </tag>) '''
        
        replacement = entry[TT_XML]   
        self.tokens.insert(0, replacement) 
      
 
    def __compileClass__(self):
        ''' compiles a class declaration.
            returning a list of VM commands. '''
        
        result = []
        result.append( '<class>' )                                                    #structure label for class
        self.indentation += 2                                                         #indentation level adjustment                                                 
        
        tokenTuple = self.__getNextEntry__()
        
        if tokenTuple[TT_TOKEN] == 'class':
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #keyword class
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #classname identifier
            
            self.st.className = tokenTuple[TT_TOKEN]                                  #save the class name in the symbol table
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #opening brace
            
            #VMW
            fieldVarNotSeen = True                                                    
        
            while True:
                tokenTuple = self.__peekAtNextEntry__()
            
                if tokenTuple[TT_TOKEN] == 'static' or tokenTuple[TT_TOKEN] == 'field':     
                    
                    #VMW
                    if fieldVarNotSeen and tokenTuple[TT_TOKEN] == 'field':
                        self.st.classVarIndex = 0
                        fieldVarNotSeen = False
                        
                    result.extend(self.__compileClassVarDec__())                                    #checks for classVarDec(s) and calls appropriate function
                
                elif tokenTuple[TT_TOKEN] == 'constructor' or tokenTuple[TT_TOKEN] == 'function' \
                    or tokenTuple[TT_TOKEN] == 'method':
                    result.extend(self.__compileSubroutine__())                                     #checks for subroutine(s) and calls appropriate function
                
                else:
                    break
                
        else:
            raise RuntimeError('Error, token provided:', tokenTuple[TT_TOKEN], ', is not class')
        
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])                 #closing brace 
        
        self.indentation -= 2                                                         #indentation level re-adjustment 
        result.append( '</class>' )                                                   #structure end label class
            
        return result


    def __compileClassVarDec__(self):
        ''' compiles a class variable declaration statement.
            returning a list of VM commands. '''
        
        result = []
        result.append((self.indentation * ' ') + '<classVarDec>' )                     #structure label for classVarDec
        self.indentation += 2                                                          #indentation level adjustment
        
        tokenTuple = self.__getNextEntry__()
                
        if tokenTuple[TT_TOKEN] == 'static' or tokenTuple[TT_TOKEN] == 'field':
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])              #keyword static/field
            category = tokenTuple[TT_TOKEN]
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])              #type identifier
            kind = tokenTuple[TT_TOKEN]
            
            tokenTuple = self.__getNextEntry__()
            result.append(  (self.indentation * ' ') + tokenTuple[TT_XML])             #varName identifier 
            symbol = tokenTuple[TT_TOKEN]
            
            self.st.addEntryClass(symbol, category, kind)                              #add the entry to the SymbolTable
            
            result.append((self.indentation * ' ') + '<SYMBOL-Defined> class.' + symbol + ' (' + \
                          category + ' ' + kind + ') = ' + self.st.getClassSymbolIndex(symbol) + ' </SYMBOL-Defined>' ) 
            
            
            while True:
                tokenTuple = self.__peekAtNextEntry__()                                #checks for multple varDecs
                            
                if tokenTuple[TT_TOKEN] == ',':
                    tokenTuple = self.__getNextEntry__()
                    result.append( (self.indentation * ' ') + tokenTuple[TT_XML])      #comma
                    
                    tokenTuple = self.__getNextEntry__()
                    result.append( (self.indentation * ' ') + tokenTuple[TT_XML])      #varName identifier
                    symbol = tokenTuple[TT_TOKEN]
                    
                    self.st.addEntryClass(symbol, category, kind)                       #add the entry to the SymbolTable
                                
                    result.append((self.indentation * ' ') + '<SYMBOL-Defined> class.' + symbol + ' (' + \
                            category + ' ' + kind + ') = ' + self.st.getClassSymbolIndex(symbol) + ' </SYMBOL-Defined>' )                     
                    
                else:
                    break
            
            tokenTuple = self.__getNextEntry__()                                       #semicolon
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])            
        
        else:
            raise RuntimeError('Error, token provided:', tokenTuple[TT_TOKEN], ', is not classVarDec')   
        
        self.indentation -= 2                                                          #indentation level re-adjustment 
        result.append( (self.indentation * ' ') + '</classVarDec>' )                   #structure end label classVarDec
                    
        return result        
        

    def __compileSubroutine__(self):
        ''' compiles a function/method.
            returning a list of VM commands. '''
        
        result = []
        result.append( (self.indentation * ' ') +'<subroutineDec>' )                  #structure label for subroutineDec
        self.indentation += 2                                                         #indentation level adjustment
        
        tokenTuple = self.__getNextEntry__()
        
        if tokenTuple[TT_TOKEN] == 'constructor' or tokenTuple[TT_TOKEN] == 'function' \
            or tokenTuple[TT_TOKEN] == 'method':
            
            
            self.st.startSubroutine()
            self.st.subroutineVarIndex = 0                                            #set varIndex in subroutine symbol table to 0
            
            
            #VMW
            if tokenTuple[TT_TOKEN] == 'method':
                self.st.addEntrySubroutine('this', 'arg', self.st.className)
             
            elif tokenTuple[TT_TOKEN] == 'constructor': 
                self.isConstructor = True
                
            elif tokenTuple[TT_TOKEN] == 'function': 
                self.isFunction = True
            
                
            result.append((self.indentation * ' ') + tokenTuple[TT_XML])              #keyword function/constructor/method
                
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #keyword (void)/type   
            
            #VMW
            if tokenTuple[TT_TOKEN] == 'void':
                self.voidFlag = True
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #subroutine name identifier
            
            #VMW
            name = tokenTuple[TT_TOKEN]
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #opening parenthesis
            
            result.extend(self.__compileParameterList__())                            #parameterList
            
            self.st.subroutineVarIndex = 0                                            #set varIndex back to 0 
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #closing parenthesis
            
            result.append((self.indentation * ' ') + '<subroutineBody>')
            self.indentation += 2                                                     #append the subroutineBody label
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #opening brace for subroutineBody
            
            while True:
                tokenTuple = self.__peekAtNextEntry__()
                if tokenTuple[TT_TOKEN] == 'var':
                    result.extend(self.__compileVarDec__())
                else:
                    break                                                             #checks for and calls appropriate function for varDecs*
            
            #VMW
            self.vmW.writeFunction(self.st.className + '.' + name, self.st.varCount('var'))
            
            if self.isConstructor:
                self.vmW.writePush('constant', self.st.varCount('field'))
                self.vmW.writeCall('Memory.alloc', 1)
                self.vmW.writePop('pointer', 0) 
                
            elif not self.isFunction:
                self.vmW.writePush('argument', 0)
                self.vmW.writePop('pointer', 0) 
                self.isFunction = False  
                  
            elif self.st.className != 'Main' and self.st.varCount('var') != 0:
                self.vmW.writePush('argument', 0)
                self.vmW.writePop('pointer', 0)
         
            result.extend(self.__compileStatements__())                               #statements
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #closing brace for subroutineBody
            
            self.indentation -= 2
            result.append((self.indentation * ' ') + '</subroutineBody>')             #closing label for subroutineBody
            
        else:
            raise RuntimeError('Error, token provided:', tokenTuple[TT_TOKEN], ', is not subroutineDec')
        

        self.indentation -= 2                                                         #indentation level re-adjustment 
        result.append( (self.indentation * ' ') + '</subroutineDec>' )                #structure end label subroutineDec
            
        return result
        


    def __compileParameterList__(self):
        ''' compiles a parameter list from a function/method.
            returning a list of VM commands. '''
        
        result = []
        result.append((self.indentation * ' ') + '<parameterList>' )                  #structure label for parameterList
        self.indentation += 2 
         
        while self.__peekAtNextEntry__()[TT_TOKEN] != ')':                            #type identifier/varName/','/ or nothing
            
            tokenTuple = self.__getNextEntry__()
            if tokenTuple[TT_TOKEN] != ',':
                
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])         #type identifier 
                
                kind = tokenTuple[TT_TOKEN]
                category = 'arg'
            
                tokenTuple = self.__getNextEntry__()
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])         #varName
                symbol = tokenTuple[TT_TOKEN]
                
                self.st.addEntrySubroutine(symbol, category, kind)                    #add the entry to the SymbolTable
                                                
                result.append((self.indentation * ' ') + '<SYMBOL-Defined> subroutine.' + symbol + ' (' + \
                    category + ' ' + kind + ') = ' + self.st.getSubroutineSymbolIndex(symbol) + ' </SYMBOL-Defined>' )                
    
        
            else:
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])         #comma
        
        self.indentation -= 2                                                         #indentation level re-adjustment 
        result.append((self.indentation * ' ') + '</parameterList>' )                 #structure end label parameterList
                        
        return result                    
    

    def __compileVarDec__(self):
        ''' compiles a single variable declaration line. 
            returning a list of VM commands. '''
        
        result = []
        result.append((self.indentation * ' ') + '<varDec>' )                         #structure label for varDec
        self.indentation += 2                                                         #indentation level adjustment
        
        tokenTuple = self.__getNextEntry__()
                
        if tokenTuple[TT_TOKEN] == 'var':
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #keyword var
            category = tokenTuple[TT_TOKEN]
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #type identifier
            kind = tokenTuple[TT_TOKEN]
            
            tokenTuple = self.__getNextEntry__()
            result.append(  (self.indentation * ' ') + tokenTuple[TT_XML])            #varName identifier  
            symbol = tokenTuple[TT_TOKEN]
            
            self.st.addEntrySubroutine(symbol, category, kind)
            
            result.append((self.indentation * ' ') + '<SYMBOL-Defined> subroutine.' + symbol + ' (' + \
                    category + ' ' + kind + ') = ' + self.st.getSubroutineSymbolIndex(symbol) + ' </SYMBOL-Defined>' )             
            
            while True:
                tokenTuple = self.__peekAtNextEntry__()                               #checks for multiple varDecs
                            
                if tokenTuple[TT_TOKEN] == ',':
                    tokenTuple = self.__getNextEntry__()
                    result.append( (self.indentation * ' ') + tokenTuple[TT_XML])     #comma
                    
                    tokenTuple = self.__getNextEntry__()
                    result.append( (self.indentation * ' ') + tokenTuple[TT_XML])     #varName identifier
                    symbol = tokenTuple[TT_TOKEN]
                    
                    self.st.addEntrySubroutine(symbol, category, kind)
                    
                    result.append((self.indentation * ' ') + '<SYMBOL-Defined> subroutine.' + symbol + ' (' + \
                            category + ' ' + kind + ') = ' + self.st.getSubroutineSymbolIndex(symbol) + ' </SYMBOL-Defined>' )                     
                    
                else:
                    break
            
            tokenTuple = self.__getNextEntry__()                                      #semicolon
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])            
        
        else:
            raise RuntimeError('Error, token provided:', tokenTuple[TT_TOKEN], ', is not varDec')   
        
        self.indentation -= 2                                                         #indentation level re-adjustment 
        result.append((self.indentation * ' ') + '</varDec>' )                        #structure end label varDec
                    
        return result   


    def __compileStatements__(self):
        ''' compiles statements.
            returning a list of VM commands. 
            assumes any leading and trailing braces are be consumed by the caller'''
        
        result = []
        result.append((self.indentation * ' ') + '<statements>' )                    #structure label for statements
        self.indentation += 2                                                        #indentation level adjustment
        
        while self.__peekAtNextEntry__()[TT_TOKEN] in STATEMENTS:                    #statement type identifier let/if/while/do/return
            
            if self.__peekAtNextEntry__()[TT_TOKEN] == 'let':                        #let - calls self.__compileLet__()
                result.extend(self.__compileLet__())
            
            elif self.__peekAtNextEntry__()[TT_TOKEN] == 'if':                       #if - calls self.__compileIf__()
                result.extend(self.__compileIf__())
                                                                       
            elif self.__peekAtNextEntry__()[TT_TOKEN] == 'while':                    #while - calls self.__compileWhile__()
                result.extend(self.__compileWhile__()) 
            
            elif self.__peekAtNextEntry__()[TT_TOKEN] == 'do':                       #do - calls self.__compileDo__()
                result.extend(self.__compileDo__()) 

            elif self.__peekAtNextEntry__()[TT_TOKEN] == 'return':                   #return - calls self.__compileReturn__()
                result.extend(self.__compileReturn__())
                
        self.indentation -= 2                                                        #indentation level re-adjustment 
        result.append((self.indentation * ' ') + '</statements>' )                   #structure end label statements
                            
        return result  
    

    def __compileDo__(self):
        ''' compiles a function/method call.
            returning a list of VM commands. '''
        
        result = []
        result.append((self.indentation * ' ') + '<doStatement>' )                   #structure label for doStatement
        self.indentation += 2                                                        #indentation level adjustment        
        
        tokenTuple = self.__getNextEntry__()                                         #keyword do
        
        if tokenTuple[TT_TOKEN] == 'do':
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])  
            
            #VMW
            self.doCalled = True            
            
            result.extend(self.__compileSubroutineCall__())                          #subroutineCall
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])            #semicolon
            
        else:
            raise RuntimeError('Error, token provided:', tokenTuple[TT_TOKEN], ', is not doStatement')   
        
        self.indentation -= 2                                                        #indentation level re-adjustment 
        result.append((self.indentation * ' ') + '</doStatement>' )                  #structure end label doStatement
                    
        return result   
    


    def __compileLet__(self):
        ''' compiles a variable assignment statement.
            returning a list of VM commands. '''
        result = []
        result.append((self.indentation * ' ') + '<letStatement>' )                   #structure label for letStatement
        self.indentation += 2                                                         #indentation level adjustment        
                
        tokenTuple = self.__getNextEntry__()                                          #keyword let
                
        if tokenTuple[TT_TOKEN] == 'let':
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])        
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #varName
            
            result.extend(self.__addUsedSymbolTags__(tokenTuple[TT_TOKEN]))           #check if variable or class in the symbol table and add XML
            
            symbol = tokenTuple[TT_TOKEN] 
            
            #VMW
            okayArray = False
            
            if self.__peekAtNextEntry__()[TT_TOKEN] == '[':
                tokenTuple = self.__getNextEntry__()
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])         #opening bracket                
                
                okayArray = True
                
                result.extend(self.__compileExpression__())                           #expression
                
                tokenTuple = self.__getNextEntry__()
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])         #closing bracket
                                        
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #equal sign
            
            result.extend(self.__compileExpression__())
                                                    
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #semicolon    
            
            #VMW
            if self.st.subroutineTableContains(symbol) and self.st.getSubroutineSymbolKind(symbol) == 'Array' \
               and okayArray:
                self.vmW.writePop('temp', 0)
                segment = 'local'
                
                if self.st.getSubroutineSymbolCategory(symbol) == 'arg':
                    segment = 'argument'                  
                                
                self.vmW.writePush(segment, self.st.getSubroutineSymbolIndex(symbol)) #whatwhat
                self.vmW.writeArithmetic('add')
                self.vmW.writePop('pointer', 1)
                self.vmW.writePush('temp', 0)
                self.vmW.writePop('that', 0)                
            
            elif self.st.subroutineTableContains(symbol):
                segment = 'local'
                
                if self.st.getSubroutineSymbolCategory(symbol) == 'arg':
                    segment = 'argument'   
                self.vmW.writePop(segment, self.st.getSubroutineSymbolIndex(symbol))  
                
            elif self.st.classTableContains(symbol):
                if self.st.getClassSymbolCategory(symbol) == 'static':
                    self.vmW.writePop('static', self.st.getClassSymbolIndex(symbol))
                else:
                    self.vmW.writePop('this', self.st.getClassSymbolIndex(symbol))
          
            okayArray = False
            
        else:
            raise RuntimeError('Error, token provided:', tokenTuple[TT_TOKEN], ', is not letStatement')   
            
        self.indentation -= 2                                                         #indentation level re-adjustment 
        result.append((self.indentation * ' ') + '</letStatement>' )                  #structure end label letStatement
                        
        return result 
    

    def __compileWhile__(self):
        ''' compiles a while loop.
            returning a list of VM commands. '''
        result = []
        result.append((self.indentation * ' ') + '<whileStatement>' )                #structure label for whileStatement
        self.indentation += 2                                                        #indentation level adjustment        
        
        tokenTuple = self.__getNextEntry__()                                         #keyword while
                
        if tokenTuple[TT_TOKEN] == 'while':
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])            #opening parenthesis
            
            #VMW
            labelNum = self.vmW.labelCounter
            self.vmW.labelCounter += 1
            self.vmW.writeLabel('WHILE_TOP_' + str(labelNum))            
            
            result.extend(self.__compileExpression__())                              #expression
            
            #VMW
            self.vmW.writeArithmetic('not')
            self.vmW.writeIf('WHILE_EXIT_' + str(labelNum))            
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])            #closing parenthesis 
            
            tokenTuple = self.__getNextEntry__() 
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])            #opening brace
            
            result.extend(self.__compileStatements__())                              #statements
            
            #VMW
            self.vmW.writeGoto('WHILE_TOP_' + str(labelNum))
            self.vmW.writeLabel('WHILE_EXIT_' + str(labelNum))            
                        
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])            #closing brace            
            
        else:
            raise RuntimeError('Error, token provided:', tokenTuple[TT_TOKEN], ', is not whileStatement')   
                    
        self.indentation -= 2                                                        #indentation level re-adjustment 
        result.append((self.indentation * ' ') + '</whileStatement>' )               #structure end label whileStatement
                                
        return result   
        


    def __compileReturn__(self):
        ''' compiles a function return statement. 
            returning a list of VM commands. '''
        
        result = []
        result.append((self.indentation * ' ') + '<returnStatement>' )                 #structure label for returnStatement
        self.indentation += 2                                                          #indentation level adjustment
                
        tokenTuple = self.__getNextEntry__()
        
        if tokenTuple[TT_TOKEN] == 'return':
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])              #keyword return
            
            if self.__peekAtNextEntry__()[TT_TOKEN] != ';':                            #expression 0 or 1 times
                result.extend(self.__compileExpression__())
        
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])              #semicolon
            
        else:
            raise RuntimeError('Error, token provided:', tokenTuple[TT_TOKEN], ', is not returnStatement')  
        
        #VMW
        if self.voidFlag: 
            self.vmW.writePush('constant', 0)
            self.voidFlag = False
            
        self.vmW.writeReturn() 
        
        self.isConstructor = False
        
        self.indentation -= 2                                                          #indentation level re-adjustment 
        result.append((self.indentation * ' ') + '</returnStatement>' )                #structure end label returnStatement
                                
        return result
    


    def __compileIf__(self):
        ''' compiles an if(else)? statement block. 
            returning a list of VM commands. '''
        result = []
        result.append((self.indentation * ' ') + '<ifStatement>' )                    #structure label for ifStatement
        self.indentation += 2                                                         #indentation level adjustment        
        
        tokenTuple = self.__getNextEntry__()                                          #keyword if
                
        if tokenTuple[TT_TOKEN] == 'if':
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #opening parenthesis
            
            result.extend(self.__compileExpression__())                               #expression
            
            #VMW
            labelNum = self.vmW.labelCounter
            self.vmW.labelCounter += 1            
            self.vmW.writeArithmetic('not')
            self.vmW.writeIf('DO_ELSE_' + str(labelNum))            
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #closing parenthesis 
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #opening brace
            
            result.extend(self.__compileStatements__())                               #statements
                        
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])             #closing brace 
            
            #VMW
            elseStatementPresent = False
            
            if self.__peekAtNextEntry__()[TT_TOKEN] == 'else':
                tokenTuple = self.__getNextEntry__()
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])         #keyword else                
                
                tokenTuple = self.__getNextEntry__()
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])         #opening brace
                
                #VMW
                self.vmW.writeGoto('IF_THEN_COMPLETE_' + str(labelNum))
                self.vmW.writeLabel('DO_ELSE_' + str(labelNum))                
                            
                result.extend(self.__compileStatements__())                            #statements
                                        
                tokenTuple = self.__getNextEntry__()
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])         #closing brace 
                
                elseStatementPresent = True
        
            #VMW           
            if not elseStatementPresent: 
                self.vmW.writeGoto('IF_THEN_COMPLETE_' + str(labelNum))
                self.vmW.writeLabel('DO_ELSE_' + str(labelNum)) 
                self.wasInDo = False
                self.wasDealingWithClassMethod = False             
            
            self.vmW.writeLabel('IF_THEN_COMPLETE_' + str(labelNum))   
            
        else:
            raise RuntimeError('Error, token provided:', tokenTuple[TT_TOKEN], ', is not ifStatement')   
                    
        self.indentation -= 2                                                         #indentation level re-adjustment 
        result.append((self.indentation * ' ') + '</ifStatement>' )                   #structure end label ifStatement
                                
        return result 
    

    def __compileExpression__(self):
        ''' compiles an expression.
            returning a list of VM commands. '''
        
        result = []
        result.append((self.indentation * ' ') + '<expression>' )                   #structure label for expression
        self.indentation += 2                                                       #indentation level adjustment        
        
        result.extend(self.__compileTerm__())                                       #term     
        
        #VMW
        termIDList = []         
        
        while self.__peekAtNextEntry__()[TT_TOKEN] in OPERATORS and self.__peekAtNextEntry__()[TT_TOKEN] != ';':                   
            
            tokenTuple = self.__getNextEntry__()                                      
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])           #checks for operator and calls self.__compileTerm__ if required  
            
            #VMW
            termIDList.append(tokenTuple[TT_TOKEN])
            
            result.extend(self.__compileTerm__())                                   #term
            
        #VMW
        if len(termIDList) > 0:
            termIDList.reverse()
            for termID in termIDList:
                if termID == '*' or termID == '/':
                    self.vmW.writeCall(BINARY_OPERATORS[termID], len(termIDList) + 1)
                else:
                    self.vmW.writeArithmetic(BINARY_OPERATORS[termID])              
        
        self.indentation -= 2                                                       #indentation level re-adjustment 
        result.append((self.indentation * ' ') + '</expression>' )                  #structure end label expression
                                        
        return result        
        

    def __compileTerm__(self):
        ''' compiles a term. 
            returning a list of VM commands. '''
        
        result = []
        result.append((self.indentation * ' ') + '<term>' )                                     #structure label for term
        self.indentation += 2
       
        tokenTuple = self.__getNextEntry__()
       
        if 'Constant' in tokenTuple[TT_XML][1:tokenTuple[TT_XML].index('>')]:                   #integerConstant or stringConstant
           
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])
            
            #VMW
            if tokenTuple[TT_TOKEN].isdigit():
                self.vmW.writePush('constant', tokenTuple[TT_TOKEN])
            
            else:
                charCount = 0
                charList = []
                for index in range(tokenTuple[TT_XML].index('>') + 2,tokenTuple[TT_XML].index('/') - 2):
                    charCount += 1
                    charList.append(tokenTuple[TT_XML][index])
                    
                self.vmW.writePush('constant', charCount)
                self.vmW.writeCall('String.new', 1)
                
                for char in charList:
                    self.vmW.writePush('constant', ord(char))
                    self.vmW.writeCall('String.appendChar', 2)
           
        elif 'keyword' == tokenTuple[TT_XML][1:tokenTuple[TT_XML].index('>')]:                  #keywordConstant
           
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])
            
            #VMW
            if tokenTuple[TT_TOKEN] == 'true':
                self.vmW.writePush('constant', '0')
                self.vmW.writeArithmetic('not')
            elif tokenTuple[TT_TOKEN] == 'false' or tokenTuple[TT_TOKEN] == 'null':
                self.vmW.writePush('constant', '0')
            elif tokenTuple[TT_TOKEN] == 'this':
                self.vmW.writePush('pointer', '0')                 
                              
       
        elif 'identifier' == tokenTuple[TT_XML][1:tokenTuple[TT_XML].index('>')]:               #varName or subroutineCall
           
            secondTokenTuple = self.__getNextEntry__()                                          #check next token to see if subroutineCall or varName 
           
            if secondTokenTuple[TT_TOKEN] == '.' or secondTokenTuple[TT_TOKEN] == '(':          #if it is a subroutineCall
               
                self.__replaceEntry__(secondTokenTuple)                                         #put secondtokenTuple back on the list
               
                self.__replaceEntry__(tokenTuple)                                               #put tokenTuple back on the list
               
                result.extend(self.__compileSubroutineCall__())                                 #calls self.__compileSubroutineCall__()
               
            elif secondTokenTuple[TT_TOKEN] == '[':                                             #if it is a varName followed by expression

                result.append( (self.indentation * ' ') + '<identifier> ' + tokenTuple[TT_TOKEN] +' </identifier>')     #varName
                
                symbol = tokenTuple[TT_TOKEN]
                
                result.extend(self.__addUsedSymbolTags__(tokenTuple[TT_TOKEN]))                 #check if variable or class in the symbol table and add XML
               
                result.append( (self.indentation * ' ') + '<symbol> ' + secondTokenTuple[TT_TOKEN] +' </symbol>')       #opening bracket
                           
                result.extend(self.__compileExpression__())                                     #calls self.__compileExpression__()
                
                #VMW
                self.vmW.writePush('local', self.st.getSubroutineSymbolIndex(symbol))
                self.vmW.writeArithmetic('add')
                self.vmW.writePop('pointer', 1)
                self.vmW.writePush('that', 0)
                
                tokenTuple = self.__getNextEntry__()          
                result.append( (self.indentation * ' ') + '<symbol> ' + tokenTuple[TT_TOKEN] +' </symbol>')             #closing bracket               
               
            else:                                                                                #if it is only a varName
               
                self.__replaceEntry__(secondTokenTuple)                                          #put secondTokenTuple back
               
                result.append( (self.indentation * ' ') + '<identifier> ' + tokenTuple[TT_TOKEN] +' </identifier>')     #varName
                
                result.extend(self.__addUsedSymbolTags__(tokenTuple[TT_TOKEN]))                  #check if variable or class in the symbol table and add XML
                
                #VMW
                symbol = tokenTuple[TT_TOKEN]
                if self.st.subroutineTableContains(symbol):
                    segment = 'local'
                    if self.st.getSubroutineSymbolCategory(symbol) == 'arg':
                        segment = 'argument'
                    self.vmW.writePush(segment, self.st.getSubroutineSymbolIndex(symbol))  
                if self.st.classTableContains(symbol):
                    if self.st.getClassSymbolCategory(symbol) == 'static': #whatwhat
                        self.vmW.writePush('static', self.st.getClassSymbolIndex(symbol))
                    else:
                        self.vmW.writePush('this', self.st.getClassSymbolIndex(symbol))
           
        elif tokenTuple[TT_TOKEN] == '(':                                                        #if it is an expression
           
            result.append( (self.indentation * ' ') + '<symbol> ' + tokenTuple[TT_TOKEN] +' </symbol>')                 #opening parenthesis
           
            result.extend(self.__compileExpression__())                                          #calls self.__compileExpression__()
           
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + '<symbol> ' + tokenTuple[TT_TOKEN] +' </symbol>')                 #closing parenthesis
       
        elif tokenTuple[TT_TOKEN] == '-' or tokenTuple[TT_TOKEN] == '~':                         #if it is a unaryOp
           
            result.append( (self.indentation * ' ') + '<symbol> ' + tokenTuple[TT_TOKEN] +' </symbol>')                 #unaryOp
           
            result.extend(self.__compileTerm__())                                                                       #calls self.__compileTerm__()
            
            #VMW
            self.vmW.writeArithmetic(UNARY_OPERATORS[tokenTuple[TT_TOKEN]])            
       
        else:
            raise RuntimeError('Error, tokenTuple provided,', tokenTuple, ', is not for term')
       
        self.indentation -= 2                                                                   #indentation level re-adjustment
        result.append((self.indentation * ' ') + '</term>' )                                    #structure end label term
                             
        return result           
        


    def __compileExpressionList__(self):
        ''' compiles a list of expressions. 
            returning a list of VM commands. '''
        
        result = []
        result.append((self.indentation * ' ') + '<expressionList>' )               #structure label for expressionList
        self.indentation += 2 
        
        #VMW       
        self.expressionCount = 0        
        
        
        while self.__peekAtNextEntry__()[TT_TOKEN] != ')':                          #expression, ",", or nothing
            if self.__peekAtNextEntry__()[TT_TOKEN] != ',':
                
                #VMW
                self.expressionCount += 1   
                
                result.extend(self.__compileExpression__())                         #if not "," then call self.__compileExpression__()
            else:
                tokenTuple = self.__getNextEntry__()
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])       #comma
        
        self.indentation -= 2                                                       #indentation level re-adjustment 
        result.append((self.indentation * ' ') + '</expressionList>' )              #structure end label expressionList
                        
        return result                    
    


    def __compileSubroutineCall__(self):
        ''' compiles a subroutine call.
            returning a list of VM commands. '''
        
        result = []
        
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])               #subroutineName or className/varName
        
        prefixName = tokenTuple[TT_TOKEN]
        
        #VMW
        if self.st.subroutineTableContains(prefixName):
            self.inMethod = True
        elif self.st.classTableContains(prefixName):
            self.inMethod = True
            self.dealingWithClassMethod = True
        elif prefixName[0].isupper:
            self.dealingWithExternalLibClassMethod = True        
            
            
        if self.__peekAtNextEntry__()[TT_TOKEN] == '.':                             #if period - indicates that first entry was className or VarName
            
            result.extend(self.__addUsedSymbolTags__(tokenTuple[TT_TOKEN]))         #check if variable or class in the symbol table and add XML
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])           #period          
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])           #subroutineName 
            
            #VMW
            newPrefixName = prefixName
            
            if self.st.subroutineTableContains(prefixName): 
                newPrefixName = self.st.getSubroutineSymbolKind(prefixName)
            if self.st.classTableContains(prefixName): 
                newPrefixName = self.st.getClassSymbolKind(prefixName)
                
            name = newPrefixName + '.' + tokenTuple[TT_TOKEN]            
             
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])           #opening parenthesis 
            
            #VMW
            if self.inMethod and self.dealingWithClassMethod: 
                self.vmW.writePush('this', self.st.getClassSymbolIndex(prefixName))            
            
            result.extend(self.__compileExpressionList__())                         #calls self.__expressionList__()
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])           #closing parenthesis            
            
            #VMW
            if self.inMethod and self.dealingWithClassMethod:
                self.vmW.writeCall(name, self.expressionCount +1)                
                
            elif self.doCalled and self.inMethod and not self.dealingWithExternalLibClassMethod: 
                self.vmW.writePush('local', 0)
                self.vmW.writeCall(name, self.expressionCount +1)
                self.dealingWithExternalLibClassMethod = False
            
            elif self.doCalled and self.inMethod:
                self.vmW.writePush('local', 0)
                self.vmW.writeCall(name, self.expressionCount +1) 
                
            else:
                self.vmW.writeCall(name, self.expressionCount)            
            

        else:                                                                       #otherwise first entry was subroutineName
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])           #opening parenthesis          
            
            #VMW
            if self.doCalled and not self.inMethod: 
                self.vmW.writePush('pointer', 0)            
            
            result.extend(self.__compileExpressionList__())                         #calls self.__expressionList__()
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])           #closing parenthesis          
            
            #VMW
            if self.doCalled and self.inMethod:
                self.vmW.writePush('local', 0)  
                self.vmW.writeCall(prefixName, self.expressionCount +1)
            elif self.doCalled:   
                self.vmW.writeCall(self.st.className + '.' + prefixName, self.expressionCount +1)  
        #VMW    
        if self.doCalled:
            self.vmW.writePop('temp', 0)
            self.doCalled = False 
            self.wasInDo = True
            
        if self.dealingWithClassMethod:
            self.dealingWithClassMethod = False
            self.wasDealingWithClassMethod = True
        
        self.inMethod = False

        return result
    
    
    def __addUsedSymbolTags__(self, symbol):
        
        result = []
        
        if self.st.subroutineTableContains(symbol):
            result.append((self.indentation * ' ') + '<SYMBOL-Used> subroutine.' + symbol + ' (' + \
                self.st.getSubroutineSymbolCategory(symbol) + ' ' + self.st.getSubroutineSymbolKind(symbol)\
                + ') = ' + self.st.getSubroutineSymbolIndex(symbol) + ' </SYMBOL-Used>' )            
            
        elif self.st.classTableContains(symbol):
            result.append((self.indentation * ' ') + '<SYMBOL-Used> class.' + symbol + ' (' + \
                self.st.getClassSymbolCategory(symbol) + ' ' + self.st.getClassSymbolKind(symbol)\
                + ') = ' + self.st.getClassSymbolIndex(symbol) + ' </SYMBOL-Used>' )            
        
        return result

    
   
