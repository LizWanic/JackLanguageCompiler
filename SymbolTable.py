#
#SymbolTable.py
#
#
# CS2002   Project 11
#
# updated on 1 December by Elizabeth Wanic
#


class SymbolTable(object):

    def __init__(self):

        self.classTable = {}
        self.subroutineTable = {}
        
        self.classVarIndex = 0
        self.subroutineVarIndex = 0
        self.className = ''


    def addEntryClass(self, symbol, category, kind):
        '''adds an entry to the class symbol table'''

        self.classTable[symbol] = [category, kind, self.classVarIndex]
        self.classVarIndex += 1
        
    def startSubroutine(self):
        '''creates a new subroutine symbol table'''
        
        self.subroutineTable = {}
        
    def varCount(self, category):
        '''keeps track of variable counts per type in subroutine or class symbol tables'''
        
        result = 0
        for item in self.subroutineTable.values():
            if category == item[0]:
                result += 1
        for item in self.classTable.values():
            if category == item[0]:
                result += 1
                
        return result
        
        
    def addEntrySubroutine(self, symbol, category, kind):
        '''adds an entry to the subroutine symbol table'''

        self.subroutineTable[symbol] = [category, kind, self.subroutineVarIndex]
        self.subroutineVarIndex += 1
        
        
    def classTableContains(self, symbol):
        '''Checks for a symbol in the class symbol table'''
   
        if (self.classTable.get(symbol) == None):
            return False
        else:
            return True
        
    
    def subroutineTableContains(self, symbol):
        '''Checks for a symbol in the subroutine symbol table'''

        if (self.subroutineTable.get(symbol) == None):
            return False
        else:
            return True
        
    
    def getClassSymbolCategory(self, symbol):
        '''Gets the category of a class variable'''
        
        return self.classTable[symbol][0]
    
        
    def getClassSymbolKind(self, symbol):
        '''Gets the kind of a class variable'''
        
        return self.classTable[symbol][1]
    
    
    def getClassSymbolIndex(self, symbol):
        '''Gets the index of a class variable'''
        
        return str(self.classTable[symbol][2])
    
        
    def getSubroutineSymbolCategory(self, symbol):
        '''Gets the category of a subroutine variable'''
        
        return self.subroutineTable[symbol][0]
    
        
    def getSubroutineSymbolKind(self, symbol):
        '''Gets the kind of a subroutine variable'''
        
        return self.subroutineTable[symbol][1]
    
            
    def getSubroutineSymbolIndex(self, symbol):
        '''Gets the index of a subroutine variable'''
        
        return str(self.subroutineTable[symbol][2])
        
        
   


