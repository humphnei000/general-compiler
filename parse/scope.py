from .tools import *
from .tokens import *
from .typeInfo import *

class Scope:
    def __init__(self,parent):
        self.parent = parent
    def searchForVarType(self,name):
        if self.parent == None:
            return None
        return self.parent.searchForVarType(name)
    def searchForFunc(self,sig):
        if self.parent == None:
            return None
        return self.parent.searchForFunc(sig)
    def searchForStruct(self,name):
        if self.parent == None:
            return None
        return self.parent.searchForStruct(name)
class ModuleScope(Scope):
    def __init__(self,funcs,structs):
        super().__init__(None)
        self.funcs = funcs
        self.structs = structs
    def __repr__(self):
        return str({
            "parent":self.parent,
            "funcs":self.funcs.reprShort(),
            "structs":self.structs
        })
    def searchForFunc(self,sig):
        if self.funcs.hasSig(sig):
            return self.funcs.getFuncBySig(sig)
        return super().searchForFunc(sig)
    def searchForStruct(self,name):
        if self.structs.hasStruct(name):
            return self.structs.getStruct(name)
        return super().searchForStruct(name)
class VariableScope(Scope):
    def __init__(self,parent,vars):
        super().__init__(parent)
        self.vars = vars
    def __repr__(self):
        return str({
            "parent":self.parent,
            "vars":self.vars
        })
    def searchForVarType(self,name):
        if self.vars.hasVar(name):
            return self.vars.getVarType(name)
        return super().searchForVarType(name)