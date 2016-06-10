class VMCode(object):
    """Parses VM CODE """
    def __init__(self):
        self.asm = []

    def load(self, filepath):
        filepath = os.path.abspath(filepath)
        self.file = open(filepath, 'w')

    def writeArithmetic(self, arg1):
        
        self.asm.append('@SP')
        # Step back on stack.
        self.asm.append('AM=M-1')

        if arg1 in ('neg', 'not'):
            # Unary operators.
            if arg1 == 'neg':
                # store negative of D back in M
                self.asm.append('M=-M')
            else:
                self.asm.append('M=!M')

        else:
            # Binary operators.

            # Get value stored at bottom of stack.
            self.asm.append('D=M')
            # Step back again.
            self.asm.append('@SP')
            self.asm.append('AM=A-1')
            
            elif arg1 == 'add':    
                # add next val on stack and store
                self.asm.append('M=D+M')
                
            elif arg1 == 'sub':
                # sub next val on stack.
                self.asm.append('M=D-M')
                # store val at bottom of stack and store

            elif arg1 == 'and':
                # bitwise and both values on the stack.
                self.asm.append('M=D&M')

            elif arg1 == 'or':
                self.asm.append('')

            elif arg1 == 'eq':
                # step back again on stack.
                self.asm.append('A=A-1')
                # and both values together.


        # increment stack back to bottom.
        self.asm.append('A=A+1')

    def writePushPop(self, commandType, arg1, arg2):
        if commandType == 'C_PUSH':
            # push <arg1> <arg2>
            if arg1 == 'constant':
                # push constant <arg2>
                self.asm.append('@%d' % arg2)
                self.asm.append('D=A')
                self.asm.append('@SP')
                self.asm.append('A=M')
                self.asm.append('M=D')
                self.asm.append('A=A+1')