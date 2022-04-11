#this is a strage module, but if I put this code in functions.py, there is a circular import, becuase functions indirectly needs expressions.py, but expressions.py needs FuncSignature
from .tools import *

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
class FuncTable:
    def __init__(self):
        self.funcs = {}
    def __repr__(self):
        return str({"funcTable":list(self.funcs.values())})
    def reprShort(self):
        return {"funcSigs":self.funcs.keys()}
    def addFunc(self,func):
        sig = func.getSignature()
        if sig in self.funcs:
            raise ParseError(f"Signature already in Function Table. Signature: {sig}",func.srcInx,func.srcFile)
        else:
            self.funcs[sig] = func
    def hasSig(self, signature):
        return signature in self.funcs
    def getFuncBySig(self,signature):
        if self.hasSig(signature):
            return self.funcs[signature]
        raise Exception("Could not find signature in function table")
    def getIter(self):
        return ((sig, self.funcs[sig]) for sig in self.funcs)