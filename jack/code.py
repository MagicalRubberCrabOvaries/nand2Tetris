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
