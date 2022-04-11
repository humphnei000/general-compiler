from .tools import *
from .tokens import *

class TypeInfo:
    @classmethod
    def fromStream(cls,strm):
        tests = [RefType,ArrayType]
        acc = BasicType.fromStream(strm)
        while strm.inRange():
            for test in tests:
                res = test.fromStream(strm,acc)
                if res != None:
                    acc = res
                    break
            else:
                raise ParseError("Unidentified type")
        return acc
    @classmethod
    def fromStreamUntil(cls,strm,until):
        acc = StreamBuilder(strm)
        while True:
            for token in until:
                if strm.matchesMono(token):
                    return cls.fromStream(acc.build())
            acc.add(strm.at())
            strm.inc()
class BasicType(TypeInfo):
    def __init__(self,name):
        self.name = name
    def __eq__(self,other):
        return type(other) == BasicType and self.name == other.name
    def __hash__(self):
        return hash(self.name)
    def __repr__(self):
        return str({"baseType":self.name})
    def makeSrc(self):
        return self.name
    def validate(self,prtScope):
        struct = prtScope.searchForStruct(self.name)
        if struct == None:
            raise ParseError("Struct of name \""+self.name+"\" does not exist",self.srcInx,self.srcFile)
    @classmethod
    def fromStream(cls,strm):
        srcInx = strm.srcInx()
        if not strm.matchesInstance([Word]):
            raise ParseError("Data type expected",srcInx,strm.srcFile)
        return addSrcInfo(
            BasicType(strm.get().word),
            srcInx,
            strm.srcFile
        )
class RefType(TypeInfo):
    def __init__(self,inner):
        self.inner = inner
    def __eq__(self,other):
        return type(other) == RefType and self.inner == other.inner
    def __hash__(self):
        return hash((self.inner,"&"))
    def __repr__(self):
        return str({"refType":self.inner})
    def makeSrc(self):
        return f"{self.inner.makeSrc()}&"
    def validate(self,prtScope):
        self.inner.validate(prtScope)
    @classmethod
    def fromStream(cls,strm,prev):
        if not strm.checkMatchesMono(Glyph("&")):
            return None
        return RefType(prev)
class ArrayType(TypeInfo):
    def __init__(self,inner,count):
        self.inner = inner
        self.count = count
    def __eq__(self,other):
        return type(other) == RefType and self.inner == other.inner and self.count == other.count
    def __hash__(self):
        return hash((self.inner,self.count))
    def __repr__(self):
        return str({"arrayType":{
            "inner":self.inner,
            "count":self.count
        }})
    def makeSrc(self):
        return f"{self.inner.makeSrc()}[{self.count}]"
    def validate(self,prtScope):
        self.inner.validate(prtScope)
    @classmethod
    def fromStream(cls,strm,prev):
        if not strm.checkMatchesMono(Glyph("[")):
            return None
        if not strm.matchesInstance(NumberLiteral):
            raise ParseError("Size of array types must be specified with a single number literal")
        count = strm.get().val
        if not strm.checkMatchesMono(Glyph("]")):
            raise ParseError("Size of array types must be specified with a single number literal")
        return ArrayType(prev,val)

class Variable:
    def __init__(self,name,typeInfo):
        self.name = name
        self.typeInfo = typeInfo
    def __repr__(self):
        return str({
            "variable":{
                "name":self.name,
                "type":self.typeInfo
            }
        })
    def makeSrc(self):
        return f"{self.name}: {self.typeInfo.makeSrc()}"
    @classmethod
    def fromStream(cls,strm,until):
        if not strm.matchesInstance([Word]):
            raise ParseError("Variable name must be word",strm.srcInx())
        name = strm.get().word

        if not strm.checkMatchesMono(Glyph(":")):
            raise ParseError("Missing \':\'")

        typeInfo = TypeInfo.fromStreamUntil(strm,until)

        return Variable(name,typeInfo)
class VarTable:
    def __init__(self):
        self.vars = {}
    def __repr__(self):
        return str({"varTable":self.vars})
    def hasVar(self,name):
        return name in self.vars
    def addVar(self,var):
        if self.hasVar(var.name):
            raise Exception("Variable name already in VarTable")
        self.vars[var.name] = var
    def getVarType(self,name):
        if self.hasVar(name):
            return self.vars[name].typeInfo
        raise Exception("Variable name not in VarTable")