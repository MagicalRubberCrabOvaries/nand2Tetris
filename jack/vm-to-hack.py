from .assembler import Assembler 
from .vmTranslator import VMTranslator

import os

def main():

    filepath = base.getFilepath()
    asmPath = os.path.join(filepath, os.path.basename(filepath) + '.asm')

    V = VMTranslator(filepath)
    A = Assembler(asmPath)

    V.translate()
    print('%s' % '.asm file generated.')
    A.assemble()
    print('%s' % '.hack file generated.\nDone.')

    sys.exit()
    quit()

if __name__ == '__main__':
    main()