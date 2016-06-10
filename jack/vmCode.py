class VMCode(object):
    """Parses VM CODE """
    def __init__(self):
        self.length = 0
        self.compare_index = 0
        self.filepath = None
        self.file = None
        
    def __len__(self):
        return self.length

    def load(self, filepath):
        """Store filepath and open file into attributes"""
        if filepath
        filepath = os.path.abspath(filepath)
        self.file = open(filepath, 'w')

    def close(self):
        self.filepath = None
        self.file.close(self)

    def write(self, *commands):
        self.length += len(commands)
        if len(command) == 1:
            self.file.write(command[0] + '\n')
        else:
            self.file.write('\n'.join(command))

    def writeArithmetic(self, arg1):
        if arg1 not in ('not', 'neg', 'and', 'or', 
            'add', 'sub', 'eq', 'gt', 'lt'):

            return

        elif arg1 == 'not':
            self.write(
                '@SP',
                'AM=M-1',
                'M=!M',
                '@SP',
                'AM=M+1'
            )
        elif arg1 == 'neg':
            self.write(
                '@SP',
                'AM=M-1',
                'M=-M',
                '@SP',
                'AM=M+1'
            )
        elif arg1 == 'add':
            self.write(
                '@SP',
                'AM=M-1',
                'D=M',
                'A=A-1',
                'M=D+M'
            )
        elif arg1 == 'sub':
            self.write(
                '@SP',
                'AM=M-1',
                'D=M',
                'A=A-1',
                'M=D-M'
            )
        elif arg1 == 'and':
            self.write(
                '@SP',
                'AM=M-1',
                'D=M',
                'A=A-1',
                'M=D&M'
            )
        elif arg1 = 'or':
            self.write(
                '@SP',
                'AM=M-1',
                'D=M',
                'A=A-1',
                'M=D+M'
            )
        elif arg1 == 'eq':
            self.write(
                '@SP',
                'AM=M-1',
                'D=M',
                'A=A-1',
                'D=D-M',
                '@TRUE_%d', % self.compare_index
                'D;JEQ',
                '(FALSE_%d)', % self.compare_index
                'D=0',
                '@END_EQ_%d', % self.compare_index
                '0;JMP',
                '(TRUE_%d)', % self.compare_index
                'D=-1',
                '(END_EQ_%d)', % self.compare_index
                '@SP',
                'A=M-1',
                'M=D'
            )
            self.compare_index += 1

        if arg1 == 'lt':
            self.write(
                '@SP',
                'AM=M-1',
                'D=M',
                'A=A-1',
                'D=D-M',
                '@TRUE_%d', % self.compare_index
                'D;JLT',
                '(FALSE_%d)', % self.compare_index
                'D=0',
                '@END_LT_%d', % self.compare_index
                '0;JMP',
                '(TRUE_%d)', % self.compare_index
                'D=-1',
                '(END_LT_%d)', % self.compare_index
                '@SP',
                'A=M-1',
                'M=D'
            )
            self.compare_index += 1
            
    def writePushPop(self, commandType, arg1, arg2):

        if commandType == 'C_PUSH':
            # push <arg1> <arg2>
            if arg1 == 'constant':
                # push constant <arg2>
                self.write(
                    '@%d' % arg2,
                    'D=A',
                    '@SP',
                    'AM=M-1',
                    'M=D',
                    '@SP',
                    'AM=M+1'
                )
