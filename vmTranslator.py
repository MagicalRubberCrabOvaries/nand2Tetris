#! python3
import jack
import os
import sys
import logging


class VMTranslator(object):

    ##################
    # Dunder Methods #
    ##################

    def __init__(self, filepath):
        # Init logger object first.

        # Create Logger with "VMTranslator"
        self.logger = logging.getLogger("VMTranslator")
        self.logger.setLevel(logging.DEBUG)
        # File handler which logs even debug messages.
        fh = logging.FileHandler('VMTranslator.log')
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level.
        ch = logging.StreamHandler(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers.
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        )
        fh.setFormatter(formatter)
        # add the handlers to the self.logger
        self.logger.addHandler(fh)

        # init basic attributes
        self.filepath = os.path.abspath(filepath)
        self.filedest = os.path.join(
            filepath,
            os.path.basename(filepath) + '.asm'
        )
        self.filename = ''
        self.asm = open(self.filedest, 'w')  # out file.
        self.parsers = []  # list of parsers.
        self.length = 0  # length of out file.
        self.compare_index = 0  # index for comparison operations.

        self.functions = []
        self.callIndex = 0

        # translate arguments into asm symbols.
        self.segment = {
            'local': 'LCL',
            'argument': 'ARG',
            'this': 'THIS',
            'that': 'THAT'
        }

        # retrieve correct jump for argument.
        self.compare = {
            'eq': 'D;JEQ',
            'lt': 'D;JGT',
            'gt': 'D;JLT'
        }

        # With logger object, announce that an Assembler has been initialized.
        self.logger.debug("Assembler initialized {}".format(self.filepath))

        # walk filepath and append VMParser object to parsers for each
        # .vm object in directory and subdirectory.
        self.logger.info("walking %s" % self.filepath)

        parsers = []  # Local var for names of vm files. Name is legacy.
        for folderName, subfolders, filenames in os.walk(self.filepath):
            self.logger.info("Now in %s" % folderName)

            for subfolder in subfolders:
                self.logger.info(
                    "SUBFOLDER OF %s: %s" % (folderName, subfolders)
                )

            for filename in filenames:
                self.logger.info(
                    'FILE INSIDE %s: %s' % (folderName, filename)
                )
                # only open files with .vm extension.
                if filename.endswith('.vm'):
                    self.logger.info('%s opened for parsing.' % (folderName + filename))
                    parsers.append(os.path.join(folderName, filename))

        parsers.sort()

        for parser in parsers:
            self.parsers.append(jack.VMParser(parser))

    def __len__(self):
        """Return length of output file"""
        return self.length

    ##################
    # Helper Methods #
    ##################

    def setFilename(self, filename):
        """Update filename attribute"""
        self.filename = filename

    def stackLabel(self, label):
        """Determine whether to use f$b or b syntax."""
        if self.functions == [] or '$' in label:
            pass
        else:
            label = '%s$%s' % (self.functions[-1], label)

        return label

    def write(self, *commands):
        """Helper method. Writes a series of strings to output
        self.write(
            '@SP',
            'A=M'
        )

        will write '@SP\nA=M\n' to the output file.
        """

        self.length += len(commands)
        if len(commands) == 1:
            self.asm.write(commands[0] + '\n')
        else:
            self.asm.write('\n'.join(commands))
            self.asm.write('\n')

    def close(self):
        """Close output file"""
        self.asm.close()

    ####################
    # Stack Operations #
    ####################

    def writeArithmetic(self, arg1):
        """Translate arithmetic commands into hack assembly"""
        if arg1 not in ('not', 'neg', 'and', 'or', 
            'add', 'sub', 'eq', 'gt', 'lt'):

            return None

        elif arg1 in ('not', 'neg'):
            self.write(
                '@SP',  # Get stack pointer
                'AM=M-1',  # Deincrement sp and A register
                # Invert if 'not' else opposite.
                '%s' % 'M=!M' if arg1 == 'not' else 'M=-M',
                '@SP',  # Get stack pointer
                'AM=M+1'  # increment stack pointer and A register
            )

        elif arg1 == 'add':
            self.write(
                '@SP',
                'AM=M-1',
                'D=M',  # retrieve top of stack.
                'A=A-1',
                'M=D+M'  # retrieve next stack entry, add, and restore.
            )

        elif arg1 == 'sub':
            self.write(
                '@SP',
                'AM=M-1',
                'D=-M', 
                'A=A-1',
                'M=D+M'
            )

        elif arg1 == 'and':
            self.write(
                '@SP',
                'AM=M-1',
                'D=M',
                'A=A-1',
                'M=D&M'
            )

        elif arg1 == 'or':
            self.write(
                '@SP',
                'AM=M-1',
                'D=M',
                'A=A-1',
                'M=D|M'
            )

        elif arg1 in ('eq', 'lt', 'gt'):
            self.write(
                '@SP',
                'AM=M-1',
                'D=M',
                'A=A-1',
                'D=D-M',
                '@TRUE_%d' % self.compare_index,
                '%s' % self.compare[arg1],
                # Implied False clause
                'D=0',
                '@END_CMP_%d' % self.compare_index,
                '0;JMP',
                '(TRUE_%d)' % self.compare_index,
                'D=-1',
                '(END_CMP_%d)' % self.compare_index,
                '@SP',
                'A=M-1',
                'M=D'
            )
            self.compare_index += 1

    def writePushPop(self, commandType, arg1, arg2):
        """Translates stack commands push and pop into hack asm"""
        if commandType not in ('C_PUSH', 'C_POP'):
            return None

        elif commandType == 'C_PUSH':
            # push <arg1> <arg2>
            if arg1 == 'constant':
                # push constant <arg2>
                self.write(
                    '@%d' % arg2,
                    'D=A',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'AM=M+1'
                )

            elif arg1 == 'temp':
                # push temp <index> onto
                self.write(
                    '@R%d' % (5 + arg2),
                    'D=M',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'AM=M+1'
                )

            elif arg1 == 'static':
                self.write(
                    '@%s.%d' % (self.filename, arg2),
                    'D=M',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'AM=M+1'
                )

            elif arg1 in ('local', 'argument', 'this', 'that'):
                self.write(
                    '@%d' % arg2,
                    'D=A',
                    '@%s' % self.segment[arg1],
                    'A=D+M',  # Go to the base + index address.
                    'D=M',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'AM=M+1'
                )

            elif arg1 == 'pointer':
                self.write(
                    '@%s' % ('THIS' if arg2 == 0 else 'THAT'),
                    'D=M',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'AM=M+1'
                )

            elif arg1 in ('LCL, ARG, THIS, THAT'):
                self.write(
                    '@%s' % arg1,
                    'D=M',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'AM=M+1'
                )
            else:
                return None

        else:  # C_POP
            if arg1 == 'temp':
                self.write(
                    '@SP',
                    'AM=M-1',
                    'D=M',
                    '@R%d' % (5 + arg2),
                    'M=D'
                )

            elif arg1 == 'static':
                self.write(
                    '@SP',
                    'AM=M-1',
                    'D=M',
                    '@%s.%d' % (self.filename, arg2),
                    'M=D'
                )

            elif arg1 in ('local', 'argument', 'this', 'that'):
                self.write(
                    '@%s' % self.segment[arg1],
                    'D=M',
                    '@%d' % arg2,
                    'D=D+A',
                    '@R13',
                    'M=D',
                    '@SP',
                    'AM=M-1',
                    'D=M',
                    '@R13',
                    'A=M',
                    'M=D'
                )

            elif arg1 == 'pointer':
                self.write(
                    '@SP',
                    'AM=M-1',
                    'D=M',
                    '@%s' % ('THIS' if arg2 == 0 else 'THAT'),
                    'M=D'
                )
            elif arg1 in ('LCL', 'ARG', 'THIS', 'THAT'):
                self.write(
                    '@SP',
                    'AM=M-1',
                    'D=M',
                    '@%s' % (arg1),
                    'M=D'
                )

            else:
                None

    #############
    # Bootstrap #
    #############

    def writeInit(self):
        """Write bootstrap code"""
        self.write(
            '@256',
            'D=A',
            '@SP',
            'M=D'
        )
        self.writeCall('Sys.init', 0)

    ################
    # Program Flow #
    ################

    def writeLabel(self, label):
        """Writes a label, meant for locals within functions.
        
        Inside function 'mult':
        >>> self.writeLabel('test_label')
        '(mult$test_label)'

        Globally:
        >>> self.writeLabel('foo')
        '(foo)'
        """
        label = self.stackLabel(label)
        self.write('(%s)' % label)

    def writeGoto(self, label):
        """Unconditional goto to label arg"""
        label = self.stackLabel(label)
        self.write(
            '@%s' % label,
            '0;JMP'
        )

    def writeIf(self, label):
        """Goto if top of stack is anything but zero"""
        label = self.stackLabel(label)
        self.write(
            '@SP',
            'AM=M-1',
            'D=M',
            '@%s' % label,
            'D;JNE'
        )

    ####################
    # Function Calling #
    ####################

    def writeCall(self, functionName, numArgs):
        """Call function

        --- Pseudo-Code ---
        push return-address
        push LCL
        push ARG
        push THIS
        push THAT
        ARG = SP-n-5
        LCL = SP
        goto (functionName)
        (return-address)

        Finally, after this call, append functionName to self.functions
        to identify functions.
        """

        label = 'return-address_%d' % self.callIndex

        self.write(
            '@%s' % label,
            'D=A',
            '@SP',
            'A=M',
            'M=D',
            '@SP',
            'AM=M+1'
        )
        self.writePushPop('C_PUSH', 'LCL', None)
        self.writePushPop('C_PUSH', 'ARG', None)
        self.writePushPop('C_PUSH', 'THIS', None)
        self.writePushPop('C_PUSH', 'THAT', None)
        self.write(
            # ARG = SP-n-5
            '@%d' % (5 + numArgs),
            'D=A',
            '@SP',
            'D=M-D',
            '@ARG',
            'M=D',
        
            # LCL = SP
            '@SP',
            'D=M',
            '@LCL',
            'M=D',
        
            # goto functionName
            '@%s' % functionName,
            '0;JMP',

            # Return declaration.
            '(%s)' % label
        )

        self.callIndex += 1

    def writeFunction(self, functionName, numLocals):
        self.functions.append(functionName)

        self.write('(%s)' % functionName)

        if numLocals > 0:
            for i in range(numLocals):
                self.writePushPop('C_PUSH', 'constant', 0)

    def writeReturn(self):
        # Return value will be at top of stack.
        # Pop into argument 0.
        # SP will be repositioned to ARG + 1
        # LCL, ARG, THIS, and THAT will then be
        # restored to previous values. 

        self.write(
            # FRAME = LCL // Frame is a temp var.
            '@LCL',
            'D=M',
            '@R13',  # FRAME
            'M=D',

            # RET = *(FRAME-5)
            '@5',
            'D=D-A',
            '@R14', # RET
            'M=D',
        
            # *ARG = pop()
            '@SP',
            'A=M',
            'D=M',
            '@ARG',
            'A=M',
            'M=D',

            # SP = ARG+1
            '@ARG',
            'D=M+1',
            '@SP',
            'M=D',
        
            # THAT = *(FRAME-1)
            '@R13',
            'D=M-1',
            '@THAT',
            'M=D',

            # THIS = *(FRAME-2)
            '@R13',
            'D=M',
            '@2',
            'D=D-A',
            '@THIS',
            'M=D',

            # ARG = *(FRAME-3)
            '@R13',
            'D=M',
            '@3',
            'D=D-A',
            '@ARG',
            'M=D',

            # LCL = *(FRAME-4)
            '@R13',
            'D=M',
            '@4',
            'D=D-A',
            '@LCL',
            'M=D',
        )

        # Set all temp registers to 0.
        for i in range(8):
            self.write(
                '@R%d' % (5 + i),
                'M=0'
            )

        self.write(
            # goto return-address.
            '@R14',
            'A=M',
            'A=M',
            '0;JMP'
        )

    #################
    # Main function #
    #################

    def translate(self):
        
        self.writeInit()  # bootstrap

        # loop over each parser for each .vm file.
        self.logger.info("Iter over parsers.")
        for parser in self.parsers:
            self.logger.info('Parser of {}'.format(parser.filepath))

            self.setFilename(parser.name)
            # iter over individual parser outputs.
            for command, commandType, arg1, arg2 in parser:
                self.logger.info('Current command: %s' % command)
                self.logger.debug('%s %s %s' % (commandType, arg1, arg2))

                # Basic vmtranslation.
                if commandType == parser.C_ARITHMETIC:
                    self.writeArithmetic(arg1)
                elif commandType in (parser.C_PUSH, parser.C_POP):
                    self.writePushPop(commandType, arg1, arg2)

                # program flow
                elif commandType == parser.C_LABEL:
                    self.writeLabel(arg1)
                elif commandType == parser.C_GOTO:
                    self.writeGoto(arg1)
                elif commandType == parser.C_IF:
                    self.writeIf(arg1)

                # function calling.
                elif commandType == parser.C_CALL:
                    self.writeCall(arg1, arg2)
                elif commandType == parser.C_RETURN:
                    self.writeReturn()
                elif commandType == parser.C_FUNCTION:
                    self.writeFunction(arg1, arg2)

        self.close()

if __name__ == '__main__':

    def exit():
        sys.exit()
        quit()

    while True:
        # Try to input filepath, keep trying until correct input
        # or 'quit' keyword.
        try:
            print("Enter filepath. Relative paths to the cwd are acceptable.")
            print("Enter 'quit' or 'q' to exit.")
            filepath = input()
            if filepath.startswith('q'):
                exit()
            elif not os.path.exists(filepath):
                raise IOError

            else:
                V = VMTranslator(filepath)

        except IOError:
            print("IOError. Enter real filepath")
            continue

        break

    V.translate()
    print(".asm file generated.")
    exit()
