from comp6502 import compFile

#from ast import literal_eval
#from parse import loadProgram
#import json

def main():
    print("Running")
    program = compFile("/home/runner/general-compiler/code/main.txt")

    with open("output.txt","w") as file:
        file.write(program)
    
    '''
    with open("debug.json","w") as jsonDump:
        jsonDump.write(json.dumps(literal_eval(str(module)),indent=2))
    '''

if __name__ == "__main__":
    main()