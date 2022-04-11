from .tools import *
from .tokens import tokenize
from .modules import *

class CompileSettings:
    def __init__(self):
        self.lumpPaths = set()
        self._loadedLumps = set()
    def markLumpLoaded(self,path):
        self.lumpPaths.remove(path)
        self._loadedLumps.add(path)
    def addLumpPath(self,path):
        if path not in self._loadedLumps:
            self.lumpPaths.add(path)
    def getUnloadedPath(self):
        for path in self.lumpPaths:
            return path
    def hasUnloadedLumps(self):
        return len(self.lumpPaths) > 0
class ModuleSettings:
    def __init__(self,absPath,compSettings):
        self.absPath = absPath
        self.compSettings = compSettings
    def addLumpPath(self,path):
        self.compSettings.addLumpPath(path)
class FileLoader:
    def __init__(self):
        self._cache = {}
    def loadPath(self,path):
        if not path.isAbsolute():
            raise Exception("Path must be absolute")
        if path not in self._cache:
            with open(path.toStr()) as file:
                self._cache[path] = file.read()
        return self._cache[path]

class FileLoaderParseErrorFiller(object):
    def __init__(self,fileLoader):
        self.fileLoader = fileLoader
        #I almost wrote fource here. I hate that spelling
    def __enter__(self):
        pass
    def __exit__(self, errType, err, traceback):
        if errType is ParseError:
            if err.inx == None:
                raise Exception("Index unspecified")
            #err.inx = strm.srcInx()
            err.fillFromFileLoader(self.fileLoader)
            raise err
class SourceParseErrorFiller(object):
    def __init__(self,source):
        self.source = source
    def __enter__(self):
        pass
    def __exit__(self, errType, err, traceback):
        if errType is ParseError:
            if err.inx == None:
                raise Exception("Index unspecified")
            #err.inx = strm.srcInx()
            err.fillFromSrc(self.source)
            raise err

def loadProgram(mainPath,extraModules=[],fileLoader=None):
    if fileLoader == None:
        fileLoader = FileLoader()
    mainPath = Path.fromStr(mainPath)

    compOpts = CompileSettings()
    compOpts.addLumpPath(mainPath)

    
    accModule = parseModule(
        '',
        ModuleSettings(
            Path(["(base)"]),
            compOpts
        )
    )
    while compOpts.hasUnloadedLumps():
        path = compOpts.getUnloadedPath()
        modOpts = ModuleSettings(path,compOpts)
        
        source = fileLoader.loadPath(path)
        #print(path.toStr())
        #print(source)
        with FileLoaderParseErrorFiller(fileLoader):
            module = parseModule(source,modOpts)
            accModule.merge(module)

        compOpts.markLumpLoaded(path)
    
    for module in extraModules:
        accModule.merge(module)
    
    with FileLoaderParseErrorFiller(fileLoader):
        accModule.validate()

    return accModule

#does not verify
def parseModule(source,compOpts=None):
    if compOpts == None:
        compOpts = ModuleSettings(Path(["<src>"]),CompileSettings())

    strm = Stream(source,False)
    strm.srcFile = compOpts.absPath.toStr()

    with SourceParseErrorFiller(source):
        strm = tokenize(strm)
        module = Module.fromStream(strm,compOpts)
        return module