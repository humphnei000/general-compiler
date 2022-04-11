from parse import loadProgram, parseModule
from parse.tools import DebugFormatter

def compFile(path):
    auxModules = []

    mainModule = loadProgram(path,auxModules)

    dbf = DebugFormatter("putSrc")
    mainModule.putSrc(dbf)

    parseModule(dbf.acc).validate()

    #print(__file__)

    return dbf.acc