from .tools import *
from .tokens import *
from .typeInfo import *

class Struct:
    def __init__(self,name,fields):
        self.name = name
        self.fields = fields
    def validate(self,prtScope):
        for field in self.fields:
            field.typeInfo.validate(prtScope)
    def __repr__(self):
        return str({
            "name":self.name,
            "fields":self.fields
        })
    def putSrc(self,dbf):
        if len(self.fields) == 0:
            dbf.putLine(f"struct {self.name} {{}}")
            return
        dbf.putLine(f"struct {self.name} {{")
        with dbf:
            for field in self.fields:
                dbf.putLine(f"{field.makeSrc()};")
        dbf.putLine("}")
    def isEmpty(self):
        return len(self.fields) == 0
    @classmethod
    def fromStream(cls,strm):
        if not strm.checkMatchesMono(Word("struct")):
            return None
        
        if not strm.matchesInstance([Word]):
            raise ParseError("Struct does not have name",strm.srcInx())
        name = strm.get().word

        #unnecessary. looks nice, but may want to rethink
        if not strm.checkMatchesMono(Glyph("{")):
            raise ParseError("Missing {",strm.srcInx())
        
        varList = []

        while not strm.checkMatchesMono(Glyph("}")):
            varList.append(Variable.fromStream(strm,[Glyph("}"),Glyph(";")]))
            strm.checkMatchesMono(Glyph(";"))
        
        return Struct(name,varList)
class StructTable:
    def __init__(self):
        self.structs = {}
    def __repr__(self):
        return str({"structTable":self.structs})
    def hasStruct(self,name):
        return name in self.structs
    def addStruct(self,struct):
        if self.hasStruct(struct.name):
            raise Exception("Struct name already in StructTable")
        self.structs[struct.name] = struct
    def getStruct(self,name):
        if self.hasStruct(name):
            return self.structs[name]
        raise Exception("Struct name not in StructTable")  
    def getIter(self):
        return ((name, self.structs[name]) for name in self.structs)