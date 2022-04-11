from .tools import *

class Word:
    def __init__(self,word=""):
        self.word = word
        self.hidden = False
    def __eq__(self,other):
        return type(other) == Word and self.word == other.word
    def __repr__(self):
        return str({'word':self.word})
class Glyph:
    def __init__(self,glyph):
        self.glyph = glyph
        self.hidden = False
    def __eq__(self,other):
        return type(other) == Glyph and self.glyph == other.glyph
    def __repr__(self):
        return str({'glyph':self.glyph})
    
    glyphList = [ #larger goes first
        ">>>=",
        
        ">>>",
        "<<=",">>=","**=","||=","&&=",
        
        "<<",">>",
        "++","--",
        "**",
        "<=",">=","==","!=",
        "||","&&",
        "^=","|=","&=","+=","-=","/=","*=","%=",

        "(",")","[","]",".",
        "^","|","&","~",
        "+","-","/","*","%",
        "<",">",
        "!",
        "?",
        "=",
        ",",

        "{","}",";",
        ":",
    ]
    @classmethod
    def fromStream(cls,strm):
        for g in cls.glyphList:
            if(strm.matches(list(g))):
                strm.inc(len(g))
                return Glyph(g)
        return None
class Comment:
    def __init__(self,text):
        self.text = text
        self.hidden = True
    def __eq__(self,other):
        return type(other) == Comment and self.text == other.text
    def __repr__(self):
        return str({'comment':self.text})
    @classmethod
    def fromStream(cls,strm):
        if not strm.checkMatches(list('//')):
            return None

        acc = ''
        while not strm.matches(list('\n')):
            acc += strm.get()
        
        return Comment(acc)
class MultiComment:
    def __init__(self,text):
        self.text = text
        self.hidden = True
    def __eq__(self,other):
        return type(other) == MultiComment and self.text == other.text
    def __repr__(self):
        return str({'multiComment':self.text})
    @classmethod
    def fromStream(cls,strm):
        if not strm.checkMatches(list('/*')):
            return None

        acc = ''
        while not strm.checkMatches(list('*/')):
            acc += strm.get()
        
        return MultiComment(acc)
class Whitespace:
    def __init__(self):
        self.hidden = True
    def __eq__(self,other):
        return type(other) == Whitespace
    def __repr__(self):
        return "\"whitespace\""
    @classmethod
    def fromStream(cls,strm):
        if strm.at() in [' ','\t','\n','\r']:
            strm.inc()
            return Whitespace()
        else:
            return None
class StringLiteral:
    def __init__(self,text):
        self.hidden = False
        self.text = text
    def __eq__(self,other):
        return type(other) == StringLiteral and other.text == self.text
    def __repr__(self):
        return str({"string":self.text})
    def makeSrc(self):
        acc = ""
        for c in self.text:
            acc += c
        return "\""+acc+"\""
    def validate(self,prtScope):
        return BasicType("string")
    
    slashChars = {
        '\"':'\"',
        'n':'\n',
        't':'\t',
        'r':'\r',
        '\\':'\\',
    }
    @classmethod
    def fromStream(cls,strm):
        if not strm.at() == "\"":
            return None
        strm.inc()
        
        acc = ""
        while not strm.at() == "\"":
            if strm.at() == "\\":
                strm.inc()
                if not strm.at() in cls.slashChars:
                    raise ParseError("Invalid String Escape")
                else:
                    acc += cls.slashChars[strm.at()]
                strm.inc()
            else:
                acc += strm.get()
        strm.inc()
        
        return StringLiteral(acc)
class NumberLiteral:
    def __init__(self,val):
        self.val = val
        self.hidden = False
    def __eq__(self,other):
        return type(other) == NumberLiteral and self.val == other.val
    def __repr__(self):
        return str({'number':self.val})
    def makeSrc(self):
        return str(self.val)
    def validate(self,prtScope):
        return BasicType("int")

    digits = ["0","1","2","3","4","5","6","7","8","9"]
    @classmethod
    def fromStream(cls,strm):
        acc = ""
        while strm.at() in cls.digits:
            acc += strm.get()
        
        if acc != "":
            return NumberLiteral(int(acc))

def tokenize(strm):
    tests = [
        Whitespace,
        MultiComment,
        Comment,
        Glyph,
        StringLiteral,
        NumberLiteral
    ]

    acc = StreamBuilder(strm)
    while strm.inRange():
        for cls in tests:
            token = cls.fromStream(strm)
            if token != None:
                acc.add(token)
                break
        else:
            if acc.size() == 0 or (not isinstance(acc.at(-1),Word)):
                acc.add(Word())
            acc.at(-1).word += strm.get()
    return acc.buildFiltered(lambda x: not x.hidden)

from .typeInfo import BasicType