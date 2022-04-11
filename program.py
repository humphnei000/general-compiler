from parse.typeInfo import *
import parse.statements

class Statement:
    @classmethod
    def fromSrcStatement(cls,statement):
        pass

class FuncSignature:
    def __init__(self,name,argTypes):
        self.name = name
        self.argTypes = argTypes
    def __eq__(self,other):
        return type(other) == FuncSignature and self.name == other.name and self.argTypes == other.argTypes
    def __hash__(self):
        return hash((self.name,tuple(self.argTypes)))
    def __repr__(self):
        return str({"funcSignature":{
            "name":self.name,
            "args":self.argTypes
        }})
    @classmethod
    def fromSrcFunc(cls,func):
        return FuncSignature(func.name, [arg.typeInfo for arg in func.args])
class Function:
    def __init__(self,signature):
        self.signature = signature
    def __repr__(self):
        return str({"function":self.signature})
    def getSignature(self):
        return self.signature
    @classmethod
    def fromSrcFunc(cls,func):
        return Function(
            FuncSignature.fromSrcFunc(func)
        )

class FuncTable:
    def __init__(self):
        self.funcs = {}
    def __repr__(self):
        return str({"funcTable":list(self.funcs.values())})
    def addFunc(self,func):
        sig = func.getSignature()
        if sig in self.funcs:
            raise Exception("Signature already in Function Tale")
        else:
            self.funcs[sig] = func
    def hasFunc(self, signature):
        return signature in self.funcs
    def getFunc(self,signature):
        if self.hasFunc(signature):
            return self.funcs[signature]
        raise Exception("Could not find signature in function table")
class VarTable:
    def __init__(self):
        self.vars = {}
    def __repr__(self):
        return str({"varTable":self.vars})
    def hasVar(self,name):
        return name in self.vars
    def addVar(self,name,typeInfo):
        if self.hasVar(name):
            raise Exception("Variable name already in VarTable")
        self.vars[name] = typeInfo
    def getVar(self,name):
        if self.hasVar(name):
            return self.vars[name]
        raise Exception("Variable name not in VarTable")
class Scope:
    def __init__(self):
        self.vars = VarTable()
        self.funcs = FuncTable()
        self.parent = None
    def __repr__(self):
        return str({"scope":{
            "vars":self.vars,
            "funcs":self.funcs
        }})

class Module:
    def __init__(self,scope):
        self.scope = scope
    def __repr__(self):
        return str({"module":self.scope})
    @classmethod
    def fromSrcModule(cls,module):
        scope = Scope()
        for srcFunc in module.funcs:
            scope.funcs.addFunc(Function.fromSrcFunc(srcFunc))
        return Module(scope)