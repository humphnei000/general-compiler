from .tools import *
from .tokens import *
from .typeInfo import *
from .statements import parseStatement
from .tables import FuncSignature
from .typeInfo import *
from .scope import *

class Function:
    def __init__(self,name,args,returnType,statement):
        self.name = name
        self.args = args
        self.returnType = returnType
        self.statement = statement
        self.scope = None
    def __repr__(self):
        return str({
            "function":{
                "name":self.name,
                "args":self.args,
                "returnType":self.returnType,
                "statement":self.statement
            }
        })
    def putSrc(self,dbf):
        acc = "func "+self.name+": "+self.returnType.makeSrc()+"("
        for arg in self.args:
            if acc[-1] != "(":
                acc += ", "
            acc += arg.makeSrc()
        acc += ") "+self.statement.makeSrc()
        dbf.putLine(acc)
    def getSignature(self):
        return FuncSignature(self.name, [arg.typeInfo for arg in self.args])
    def validate(self,prtScope):
        self.returnType.validate(prtScope)
        vars = VarTable()
        for arg in self.args:
            arg.typeInfo.validate(prtScope)
            vars.addVar(arg)
        self.scope = VariableScope(prtScope,vars)
        actualRetType = self.statement.validate(self.scope)
        if actualRetType == None:
            actualRetType = BasicType("void")

        #come to think of it, I could add return type assumption easily...
        if actualRetType != self.returnType:
            raise CompileException(f"Return type {self.returnType} does not match with found return type of {actualRetType} in function {self.getSignature()}")
    @classmethod
    def fromStream(cls,strm):
        srcInx = strm.srcInx()

        if not strm.checkMatchesMono(Word("func")):
            return None
        
        if not strm.matchesInstance([Word]):
            raise ParseError("Function must have a name")
        name = strm.get().word
        
        if not strm.checkMatchesMono(Glyph(":")):
            raise ParseError("Missing \':\'",strm.srcInx())
        
        returnType = TypeInfo.fromStreamUntil(strm,[Glyph("(")])
        strm.inc()

        args = []
        while not strm.checkMatchesMono(Glyph(")")):
            if not strm.matchesInstance([Word]):
                raise ParseError("Function argument name must be word")
            argName = strm.get().word

            if not strm.checkMatchesMono(Glyph(":")):
                raise ParseError("Missing \':\'")

            argType = TypeInfo.fromStreamUntil(strm,[Glyph(")"),Glyph(",")])

            strm.checkMatchesMono(Glyph(","))

            args.append(Variable(argName,argType))
        statement = parseStatement(strm)

        out = Function(name, args, returnType, statement)
        out.srcInx = srcInx
        out.srcFile = strm.srcFile
        return out