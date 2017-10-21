#
# VMWriter.py
#
# CS2002   Project 11 VM Writer 
#
# last updated 1 December 2016 by Elizabeth Wanic
#
# this file writes the lines of code for the .vm file
#

import sys  #for grading server
from pathlib import *

from SymbolTable import *
from JTConstants import *

class VMWriter(object):
    
    def __init__(self, symbolTable):
        
        self.st = symbolTable
        self.vmCodeList = []
        self.labelCounter = 0
        
    def setLabelCounter(self, count): 
        '''sets counter for labels'''
        self.labelCounter = count    
        
    def writePush(self, segment, index):
        '''writes a push command'''
        self.vmCodeList.append('push ' + segment + ' ' + str(index))
    
    
    def writePop(self, segment, index):
        '''writes a pop command'''
        self.vmCodeList.append('pop ' + segment + ' ' + str(index))
        
    
    def writeArithmetic(self, command):
        '''writes an arithmetic command'''
        self.vmCodeList.append(command)


    def writeLabel(self, label):
        '''writes a label vm line'''
        self.vmCodeList.append('label ' + label)
    
    
    def writeGoto(self, label):
        '''writes a goto label'''
        self.vmCodeList.append('goto ' + label)

    
    def writeIf(self, label):
        '''writes an if label'''
        self.vmCodeList.append('if-goto ' + label)
    
    
    def writeCall(self, name, nArgs):
        '''writes a call command'''
        self.vmCodeList.append('call ' + name + ' ' + str(nArgs))
    
    
    def writeFunction(self, name, nLocals):
        '''writes a function command'''
        self.vmCodeList.append('function ' + name + ' ' + str(nLocals))
    
    
    def writeReturn(self):
        '''writes a return command'''
        self.vmCodeList.append('return')


    def get_VMCodeList(self):
        '''returns a fully translated list of VM instructions'''
        return self.vmCodeList