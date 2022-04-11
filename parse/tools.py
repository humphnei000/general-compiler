def addSrcInfo(obj,inx,file):
    obj.inx = inx
    obj.file = file
    return obj

class DebugFormatter:
    def __init__(self,funcName):
        self.funcName = funcName
        self.acc = ""
        self.indent = 0
    def pushIndent(self):
        self.indent += 1
    def popIndent(self):
        self.indent -= 1
    def putLine(self,txt):
        if self.acc != "":
            self.acc += "\n"
        self.acc += ("  "*self.indent) + txt
    def __enter__(self):
        self.pushIndent()
    def __exit__(self,errType,err,traceback):
        self.popIndent()
class ModulePath:
    def __init__(self,path):
        self.path = path
    def __eq__(self,other):
        return type(other) == ModulePath and self.path == other.path
    def __hash__(self):
        return hash(tuple(self.path))
    def makeAbsPath(self,rel):
        if self.path[0] != "":
            raise Exception("This path is not absolute")
        
        out = self.clone()
        for folder in rel.path:
            if folder == "..":
                if "." in out.path[-1]:
                    out.path.pop()
                out.path.pop()
            elif folder == "":
                raise Exception("Blank folders are illegal")
            elif folder == ".":
                if "." in out.path[-1]:
                    out.path.pop()
            else:
                out.path.append(folder)
        return out
    def toStr(self):
        return '/'.join(self.path)
    def clone(self):
        return ModulePath([el for el in self.path])
    def isAbsolute(self):
        return self.path[0] == ""
    @classmethod
    def fromStr(cls,string):
        path = string.split('/')
        if not path[0] in ['','.','..']:
            path = ["."] + path
        return ModulePath(path)
Path = ModulePath

class CompileException(Exception): pass
class ParseError(CompileException):
    def __init__(self,message,inx=None,file=None):
        self.inx = inx
        self.file = file
        self.line = None
        self.col = None
        self.msg = message
        super().__init__(message)
    def fillFromSrc(self,src):
        i = 0
        self.line = 1
        self.col = 1

        while i != self.inx:
            if src[i] == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            i += 1
    def fillFromFileLoader(self,loader):
        path = ModulePath.fromStr(self.file)
        self.fillFromSrc(loader.loadPath(path))
    def __str__(self):
        return f"At line {self.line}, column {self.col} in file {self.file}:\n{self.msg}"

class Stream:
    def __init__(self,data,objInx=True):
        self.data = list(data)
        self.objInx = objInx
        self.eofError = False
        self.inx = 0
    def inxInRange(self,inx):
        return inx >= 0 and inx < len(self.data)
    def at(self,i=0):
        inx = self.inx+i
        if self.eofError and (not self.inxInRange(inx)):
            raise ParseError("Unexpected EOF")
        return self.data[inx]
    def atRange(self,a=0,b=1):
        return self.data[self.inx+a:self.inx+b]
    def inc(self,i=1):
        self.inx += i
    def dec(self,i=1):
        self.inc(-i)
    def gotoEnd(self):
        self.inx = len(self.data)-1
    def get(self):
        res = self.at()
        self.inc()
        return res
    def inRange(self):
        return self.inxInRange(self.inx)
    def __repr__(self):
        return str({'list':self.data})
    
    def matches(self,l):
        return self.atRange(0,len(l)) == l
    def checkMatches(self,l):
        if self.matches(l):
            self.inc(len(l))
            return True
        return False
    def matchesMono(self,o):
        return self.at() == o
    def checkMatchesMono(self,o):
        if self.matchesMono(o):
            self.inc()
            return True
        return False
    def matchesInstance(self,l):
        selfItems = self.atRange(0,len(l))
        if len(selfItems) == len(l):
            for i in range(len(l)):
                if not isinstance(selfItems[i],l[i]):
                    return False
            return True
        else:
            return False
    def srcInx(self):
        if self.objInx:
            return self.data[self.inx].srcInx;
        else:
            return self.inx
class StreamBuilder:
    def __init__(self,srcStrm):
        self.srcStrm = srcStrm
        self.data = []
    def add(self,data,srcInx=None,srcFile=None):
        if srcInx == None:
            srcInx = self.srcStrm.srcInx()
        if srcFile == None:
            srcFile = self.srcStrm.srcFile
        self.data.append(data)
        data.srcInx = srcInx
        data.srcFile = srcFile
    def at(self,i):
        return self.data[i]
    def setAt(self,i,item):
        self.data[i] = item
    def last(self):
        return self.at(-1)
    def setLast(self,item):
        item.srcInx = self.srcStrm.srcInx()
        self.setAt(-1,item)
    def size(self):
        return len(self.data)
    def build(self):
        strm = Stream(self.data)
        strm.srcFile = self.srcStrm.srcFile
        return strm
    def buildFiltered(self,func):
        strm = Stream(filter(func,self.data))
        strm.srcFile = self.srcStrm.srcFile
        return strm
    def buildReversed(self):
        strm = Stream(reversed(self.data))
        strm.srcFile = self.srcStrm.srcFile
        return strm