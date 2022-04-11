from .tools import *
from .typeInfo import *
from .tokens import *
from .scope import *
from .tables import FuncTable
from .functions import Function
from .structs import *

class Lump:
    def __init__(self,path):
        self.path = path
    def addPath(self,modOpts):
        path = self.path.clone()
        if not path.isAbsolute():
            path = modOpts.absPath.makeAbsPath(path)
        modOpts.addLumpPath(path)
    @classmethod
    def fromStream(cls,strm):
        if not strm.checkMatchesMono(Word("lump")):
            return None
        if not strm.matchesInstance([StringLiteral]):
            raise ParseError("Lump path must be specified by string literal",strm.srcInx())
        path = ModulePath.fromStr(strm.get().text)
        return Lump(path)

class Module:
    def __init__(self,funcs,structs):
        self.funcs = funcs
        self.structs = structs
        self.scope = None
    def __repr__(self):
        return str({
            "module":{
                "funcs":self.funcs,
                "structs":self.structs,
            }
        })
    def putSrc(self,dbf):
        lastStruct = None
        for name, struct in self.structs.getIter():
            if not ((lastStruct == None or lastStruct.isEmpty()) and struct.isEmpty()):
                dbf.putLine("")
            struct.putSrc(dbf)
        for sig, func in self.funcs.getIter():
            func.putSrc(dbf)
    #only call validate after merging everything
    def validate(self):
        self.scope = ModuleScope(self.funcs,self.structs)
        for sig, func in self.funcs.getIter():
            func.validate(self.scope)
        for name, struct in self.structs.getIter():
            struct.validate(self.scope)
    def merge(self, other):
        for sig, func in other.funcs.getIter():
            self.funcs.addFunc(func)
        for name, struct in other.structs.getIter():
            self.structs.addStruct(struct)
    @classmethod
    def fromStream(cls,strm,modOpts):
        tests = [
            Function,
            Struct,
            Lump
        ]

        funcs = FuncTable()
        structs = StructTable()
        while strm.inRange():
            for test in tests:
                res = test.fromStream(strm)
                if isinstance(res,Function):
                    funcs.addFunc(res)
                    break
                elif isinstance(res,Struct):
                    structs.addStruct(res)
                    break
                elif isinstance(res,Lump):
                    res.addPath(modOpts)
                    break
            else:
                raise ParseError("Unrecognized module structure",strm.srcInx())
        return Module(funcs,structs)