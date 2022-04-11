from .tools import *
from .expressions import *
from .tokens import *
from .typeInfo import *
from .scope import *

class ExpressionStatement:
    def __init__(self,expr):
        self.expr = expr
    def __repr__(self):
        return str({"expressionStatement":self.expr})
    def putSrc(self,dbf):
        dbf.putLine(self.expr.makeSrc(True)+";")
    def validate(self,prtScope):
        self.expr.validate(prtScope)
    @classmethod
    def fromStream(cls,strm):
        return ExpressionStatement(
            Group.fromStream(strm,[Glyph(";")])
        )
class MultiStatement:
    def __init__(self,inner):
        self.inner = inner
        self.scope = None
    def __repr__(self):
        return str({"multiStatement":self.inner})
    def makeSrc(self):
        dbf = DebugFormatter("putSrc")
        self.putSrc(dbf)
        return dbf.acc
    def putSrc(self,dbf):
        dbf.putLine("{")
        with dbf:
            for stat in self.inner:
                stat.putSrc(dbf)
        dbf.putLine("}")
    def validate(self,prtScope):
        self.scope = VariableScope(prtScope,VarTable())
        totalRetType = None
        for stat in self.inner:
            retType = stat.validate(self.scope)
            if retType != None:
                if totalRetType == None:
                    totalRetType = retType
                elif totalRetType != retType:
                    raise CompileException(f"Conflicting return types of {totalRetType} and {retType}")
        return totalRetType
    @classmethod
    def fromStream(cls,strm):
        if not strm.checkMatchesMono(Glyph("{")):
            return None
        
        acc = []
        while not strm.checkMatchesMono(Glyph("}")):
            acc.append(parseStatement(strm))
        
        return MultiStatement(acc)
class IfStatement:
    def __init__(self,test,statement):
        self.test = test
        self.statement = statement
    def __repr__(self):
        return str({"ifStatement":{"test":self.test,"statement":self.statement}})
    def validate(self,prtScope):
        self.statement.validate(prtScope)
        self.test.validate(prtScope)
    @classmethod
    def fromStream(cls,strm):
        if not strm.checkMatchesMono(Word("if")):
            return None
        
        test = Group.fromStream(strm,[Glyph(";")])
        statement = parseStatement(strm)

        return IfStatement(test,statement)
class ReturnStatement:
    def __init__(self,expr):
        self.expr = expr
    def __repr__(self):
        return str({"returnStatement":self.expr})
    def putSrc(self,dbf):
        dbf.putLine("return "+self.expr.makeSrc(True)+";")
    def validate(self,prtScope):
        retTypes = self.expr.validate(prtScope)

        #change to ParseError
        if len(retTypes) != 1:
            raise CompileError("Return statement must return one value")
        
        return retTypes[0]
    @classmethod
    def fromStream(cls,strm):
        if not strm.checkMatchesMono(Word("return")):
            return None
        
        return ReturnStatement(Group.fromStream(strm,[Glyph(";")]))
class WhileStatement:
    def __init__(self,test,statement):
        self.test = test
        self.statement = statement
    def __repr__(self):
        return str({"whileStatement":{"test":self.test,"statement":self.statement}})
    def validate(self,prtScope):
        self.test.validate(prtScope)
        self.statement.validate(prtScope)
    @classmethod
    def fromStream(cls,strm):
        if not strm.checkMatchesMono(Word("while")):
            return None
        
        test = Group.fromStream(strm,[Glyph(";")])
        statement = parseStatement(strm)

        return WhileStatement(test,statement)
class DeclareStatement:
    def __init__(self,var,expr):
        self.var = var
        self.expr = expr
    def __repr__(self):
        return str({
            "declareStatement":{
                "name":self.var.name,
                "type":self.var.typeInfo,
                "expression":self.expr
            }
        })
    def validate(self,prtScope):
        if self.expr != None:
            exprType = self.expr.validate(prtScope)
            if len(exprType) != 1:
                raise ParseError("Expression with more than one result")
            exprType = exprType[0]
            if isinstance(exprType,list):
                raise ParseError("First expression is multiple types")
            sig = FuncSignature(
                Assign.funcName,
                [
                    RefType(self.var.typeInfo),
                    exprType
                ]
            )
            #print(sig)
            if prtScope.searchForFunc(sig) == None:
                raise CompileException("Assignment operator missing. Signature: "+str(sig))
        prtScope.vars.addVar(self.var)
    @classmethod
    def fromStream(cls,strm):
        if not strm.checkMatchesMono(Word("var")):
            return None
        
        if not strm.matchesInstance([Word]):
            raise ParseException("Function must be named with word")
        name = strm.get().word;
        if not strm.checkMatchesMono(Glyph(":")):
            raise ParseError("Missing \':\'")
        
        typeInfo = TypeInfo.fromStreamUntil(strm,[Glyph("="),Glyph(";")])

        if strm.checkMatchesMono(Glyph("=")):
            expr = Group.fromStream(strm,[Glyph(";")])
            return DeclareStatement(Variable(name,typeInfo),expr)
        elif strm.checkMatchesMono(Glyph(";")):
            return DeclareStatement(Variable(name,typeInfo),None)
        else:
            raise ParseError("Missing \'=\' or \';\'")

class ForStatement:
    def __init__(self,init,test,inc,statement):
        self.init = init
        self.test = test
        self.inc = inc
        self.statement = statement
    def __repr__(self):
        return str({"forStatement":{
            "init":self.init,
            "test":self.test,
            "inc":self.inc,
            "statement":self.statement}})
    def validate(self,prtScope):
        self.init.validate(prtScope)
        self.test.validate(prtScope)
        self.inc.validate(prtScope)
        self.statement.validate(prtScope)
    @classmethod
    def fromStream(cls,strm):
        if not strm.checkMatchesMono(Word("for")):
            return None
        
        init = parseStatement(strm)
        test = Group.fromStream(strm,[Glyph(";")])
        inc = parseStatement(strm)
        statement = parseStatement(strm)

        return ForStatement(init,test,inc,statement)
class BreakStatement:
    def __init__(self):
        pass
    def __repr__(self):
        return str("\"breakStatement\"")
    def validate(self):
        return
    @classmethod
    def fromStream(cls,strm):
        if not strm.checkMatchesMono(Word("break")):
            return None
        if not strm.checkMatchesMono(Glyph(";")):
            raise ParseError("Missing \';\'")
        return BreakStatement()

def parseStatement(strm):
    tests = [
        DeclareStatement,
        ReturnStatement,
        IfStatement,
        WhileStatement,
        ForStatement,
        BreakStatement,
        MultiStatement,
        ExpressionStatement
    ]

    for cls in tests:
        statement = cls.fromStream(strm)
        if statement != None:
            return statement
    else:
        raise ParseError("Statement not found")