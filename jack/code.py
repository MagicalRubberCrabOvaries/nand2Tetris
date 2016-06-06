class AssemblyCode(object):

    def __init__(self):

        self.D_BITS = {
            'A': '100',
            'D': '010',
            'M': '001',
            'AD': '110',
            'AM': '101',
            'MD': '011',
            'AMD': '111'
        }

        self.J_BITS = {
            'JMP': '111',
            'JEZ': '010',
            'JLT': '100',
            'JLE': '110',
            'JGT': '001',
            'JGE': '011',
            'JNE': '101'
        }

        self.C_BITS = {
            '0': '101010',
            '1': '111111',
            '-1': '111010',
            'D': '001100',
            'A': '110000',
            'M': '110000',
            '!D': '001101',
            '!A': '110001',
            '!M': '110001',
            '-D': '001111',
            '-A': '110011',
            '-M': '110011',
            'D+1': '011111',
            'A+1': '110111',
            'M+1': '110111',
            'D-1': '001110',
            'A-1': '110010',
            'M-1': '110010',
            'D+A': '000010',
            'D+M': '000010',
            'D-A': '010011',
            'D-M': '010011',
            'A-D': '000111',
            'M-D': '000111',
            'D&A': '000000',
            'D&M': '000000',
            'D|A': '010101',
            'D|M': '010101'
        }

    def dest(self, mnemonic):
        if mnemonic is None:
            return '000'
        return self.D_BITS[mnemonic]

    def comp(self, mnemonic):
        return self.C_BITS[mnemonic]

    def jump(self, mnemonic):
        if mnemonic is None:
            return '000'
        return self.J_BITS[mnemonic]


class VMCode(object):
    """Parses VM CODE """
    def __init__(self):
        self.asm = []

    def writeArithmetic(self, arg1):
        
        # assumes A is already bottom of stack.
        # Step back on stack.
        self.asm.append('A=A-1')
        # Retrieve stack value and store in D.
        self.asm.append('D=M')

        if arg1 == 'neg':
            # store negative of D back in M
            self.asm.append('M=-D')

        elif arg1 == 'add':
            # step back again on stack.
            self.asm.append('A=A-1')
            # add next val on stack.
            self.asm.append('D=D+M')
            # store val at bottom of stack.
            self.asm.append('M=D')

        elif arg1 == 'sub':
            # step back again on stack.
            self.asm.append('A=A-1')
            # sub next val on stack.
            self.asm.append('D=D-M')
            # store val at bottom of stack.
            self.asm.append('M=D')

        elif arg1 == 'eq':
            # step back again on stack.
            self.asm.append('A=A-1')
            # add next val on


        # increment stack back to bottom.
        self.asm.append('A=A+1')

    def writePushPop(self, commandType arg1, arg2):
        if commandType == 'C_PUSH':
            # push <arg1> <arg2>
            if arg1 == 'constant':
                # push constant <arg2>
                self.asm.append('@%d' % arg2)
                self.asm.append('D=A')
                self.asm.append('@SP')
                self.asm.append('M=D')
                self.asm.append('A=A+1')