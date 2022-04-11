from .tools import *
from .tokens import *
from .tables import FuncSignature
from .typeInfo import *

class Expression:
    pass
class FuncCall(Expression):
    def __init__(self,ident,args):
        self.ident = ident
        self.args = args
    def __repr__(self):
        return str({"function call":{"ident":self.ident,"args":self.args}})
    def makeSrc(self):
        return self.ident.name+"("+self.args.makeSrc(True)+")"
    def validate(self,prtScope):
        #self.ident.validate(prtScope)
        argTypes = self.args.validate(prtScope)
        sig = FuncSignature(self.ident.name,argTypes)

        func = prtScope.searchForFunc(sig)
        if func == None:
            raise ParseError("Could not find function signature in current scope. Signature: "+str(sig),self.srcInx,self.srcFile)
        return func.returnType
class Identifier(Expression):
    def __init__(self,name):
        self.name = name
    def __repr__(self):
        return str({"identifier":self.name})
    def validate(self,prtScope):
        varType = prtScope.searchForVarType(self.name)
        if varType == None:
            print(prtScope,self.name)
            raise ParseError("Could not find identifier in current scope",self.srcInx,self.srcFile)
        return RefType(varType)
class Boolean(Expression):
    def __init__(self,val):
        self.val = val
    def __repr__(self):
        return str({"boolean":self.val})
    def makeSrc(self):
        if self.val:
            return "true"
        else:
            return "false"
    def validate(self,prtScope):
        return BasicType("bool")
class BiExpr(Expression):
    def __init__(self,left,right):
        self.left = left
        self.right = right
        #self.mnemonic defined as class variable
    def __repr__(self):
        d = {}
        d[self.mnemonic] = {"left":self.left,"right":self.right}
        return str(d)
    def validate(self,prtScope): #will need extending
        argA = self.left.validate(prtScope)
        argB = self.right.validate(prtScope)
        sig = FuncSignature(self.funcName,[argA,argB])

        func = prtScope.searchForFunc(sig)
        if func == None:
            raise ParseError("Could not find function signature in current scope. Signature: "+str(sig),self.srcInx)
        return func.returnType

class Divide(BiExpr):
    menmonic = "divide"
    funcName = "__op_div"
class Multiply(BiExpr):
    mnemonic = "multiply"
    funcName = "__op_mult"
class Subtract(BiExpr):
    mnemonic = "subtract"
    funcName = "__op_sub"
class Add(BiExpr):
    mnemonic = "add"
    funcName = "__op_add"
class Assign(BiExpr):
    mnemonic = "assign"
    funcName = "__op_set"
class Negate(Expression):
    def __init__(self,expr):
        self.expr = expr
    def __repr__(self):
        return str({"negate":self.expr})
class MoreThan(BiExpr):
    mnemonic = "moreThan"
    funcName = "__op_mt"
class LessThan(BiExpr):
    mnemonic = "lessThan"
    funcName = "__op_lt"
class MoreThanOrEq(BiExpr):
    mnemonic = "moreThanOrEq"
    funcName = "__op_mte"
class LessThanOrEq(BiExpr):
    mnemonic = "lessThanOrEq"
    funcName = "__op_lte"
class Group(Expression):
    def __init__(self,data):
        self.data = data
    def __repr__(self):
        return str({"group":self.data})
    def makeSrc(self,atTop=False):
        acc = ", ".join([expr.makeSrc() for expr in self.data])
        if not atTop:
            acc = f"({acc})"
        return acc
    def validate(self,prtScope):
        return [expr.validate(prtScope) for expr in self.data]

    @classmethod
    def collapseBools(cls,strm):
        acc = StreamBuilder(strm)
        while strm.inRange():
            if isinstance(strm.at(0),Word):
                if strm.at().word == "true":
                    acc.add(Boolean(True))
                    strm.inc()
                    continue
                elif strm.at().word == "false":
                    acc.add(Boolean(False))
                    strm.inc()
                    continue
            acc.add(strm.at())
            strm.inc()
        return acc.build()
    @classmethod
    def collapseIdents(cls,strm):
        acc = StreamBuilder(strm)
        while strm.inRange():
            if isinstance(strm.at(0),Word):
                acc.add(Identifier(strm.at().word))
                strm.inc()
            else:
                acc.add(strm.at())
                strm.inc()
        return acc.build()
    @classmethod
    def collapseFuncs(cls,strm):
        acc = StreamBuilder(strm)
        while strm.inRange():
            if strm.matchesInstance([Identifier,Group]):
                acc.add(FuncCall(strm.at(0),strm.at(1)))
                strm.inc(2)
            else:
                acc.add(strm.at())
                strm.inc()
        return acc.build()
    @classmethod
    def collapseNegate(cls,strm):
        acc = StreamBuilder(strm)
        if strm.matchesInstance([Glyph,Expression]):
            if strm.at() == Glyph("-"):
                acc.add(Negate(strm.at(1)))
                strm.inc(2)
        while strm.inRange():
            acc.add(strm.at())
            strm.inc()
        return acc.build()
    @classmethod
    def collapseLeftToRight(cls,strm,spec):
        acc = StreamBuilder(strm)
        while strm.inRange():
            for glyph, op in spec:
                if strm.at() == glyph:
                    acc.setLast(op(acc.last(),strm.at(1)))
                    strm.inc(2)
                    break
            else:
                acc.add(strm.at())
                strm.inc()
        return acc.build()
    @classmethod
    def collapseMultDiv(cls,strm):
        acc = StreamBuilder(strm)
        while strm.inRange():
            if strm.at() == Glyph("*"):
                acc.setLast(Multiply(acc.last(),strm.at(1)))
                strm.inc(2)
            elif strm.at() == Glyph("/"):
                acc.setLast(Divide(acc.last(),strm.at(1)))
                strm.inc(2)
            else:
                acc.add(strm.at())
                strm.inc()
        return acc.build()
    @classmethod
    def collapseAddSub(cls,strm):
        acc = StreamBuilder(strm)
        while strm.inRange():
            if strm.at() == Glyph("-"):
                acc.setLast(Subtract(acc.last(),strm.at(1)))
                strm.inc(2)
            elif strm.at() == Glyph("+"):
                acc.setLast(Add(acc.last(),strm.at(1)))
                strm.inc(2)
            else:
                acc.add(strm.at())
                strm.inc()
        return acc.build()
    @classmethod
    def collapseIneq(cls,strm):
        return cls.collapseLeftToRight(strm,[
            (Glyph(">"),MoreThan),
            (Glyph("<"),LessThan),
            (Glyph(">="),MoreThanOrEq),
            (Glyph("<="),LessThanOrEq)
        ])
    @classmethod
    def collapseAssignment(cls,strm):
        strm.gotoEnd()
        acc = StreamBuilder(strm)
        while strm.inRange():
            if strm.at() == Glyph("="):
                acc.setLast(Assign(strm.at(-1),acc.last()))
                strm.dec(2)
            else:
                acc.add(strm.at())
                strm.dec()
        return acc.buildReversed()
    @classmethod
    def collapseGroups(cls,strm,until):
        acc = StreamBuilder(strm)
        while not strm.checkMatches(until):
            if strm.checkMatchesMono(Glyph("(")):
                acc.add(Group.fromStream(strm, [Glyph(")")]))
            else:
                acc.add(strm.at())
                strm.inc()
        return acc.build()
    @classmethod
    def makeGroup(cls,strm):
        acc = []
        if strm.inRange():
            while True:
                if not strm.inRange():
                    raise ParseError("Comma not succeded by expression in group")
                acc.append(strm.at())
                strm.inc()
                if not strm.inRange():
                    break
                if not strm.checkMatchesMono(Glyph(",")):
                    raise ParseError("Missing comma in group.\nStream: "+str(strm))
        return Group(acc)
    @classmethod
    def fromStream(cls,strm,until):
        strm = cls.collapseGroups(strm,until)
        strm = cls.collapseBools(strm)
        strm = cls.collapseIdents(strm)
        strm = cls.collapseFuncs(strm)
        strm = cls.collapseNegate(strm)
        strm = cls.collapseMultDiv(strm)
        strm = cls.collapseAddSub(strm)
        strm = cls.collapseIneq(strm)
        strm = cls.collapseAssignment(strm)
        return cls.makeGroup(strm)