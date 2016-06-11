#! python3
import jack
import os
import sys
import logging


class VMTranslator(object):

	def __init__(self, filepath):
		# Init logger object first.

        # Create Logger with "VMTranslator"
        self.logger = logging.getLogger("VMTranslator")
        self.logger.setLevel(logging.DEBUG)
        # File handler which logs even debug messages.
        fh = logging.FileHandler('VMTranslator.log')
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level.
        ch = logging.StreamHandler(logging.ERROR)
        ch.setLevel(logging.ERROR)
        # create formatter and add it to the handlers.
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        )
        fh.setFormatter(formatter)
        # add the handlers to the self.logger
        self.logger.addHandler(fh)

        # init basic attributes
        self.filepath = os.path.abspath(filepath)
        self.parsers = []
        self.length = 0
        self.compare_index = 0

        # With logger object, announce that an Assembler has been initialized.
        self.logger.debug("Assembler initialized {}".format(self.filepath))

        # walk filepath and append VMParser object to parsers for each
        # .vm object in directory and subdirectory.
        self.logger.info("walking {}" self.filepath)

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
        		
        		if filename.endswith('.vm'):
        			self.logger.info('%s opened for parsing.' % filename)
        			self.parsers.append(jack.VMParser(filename, isFile=True))

    def __len__(self):
        
        return self.length

    def setFilename(self, filename):
    	self.filename = filename

    def write(self, *commands):
        self.length += len(commands)
        if len(command) == 1:
            self.asm.write(command[0] + '\n')
        else:
            self.asm.write('\n'.join(command))

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

        elif arg1 == 'lt':
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

        elif arg1 == 'gt':
            self.write(
                '@SP',
                'AM=M-1',
                'D=M',
                'A=A-1',
                'D=D-M',
                '@TRUE_%d', % self.compare_index
                'D;JGT',
                '(FALSE_%d)', % self.compare_index
                'D=0',
                '@END_GT_%d', % self.compare_index
                '0;JMP',
                '(TRUE_%d)', % self.compare_index
                'D=-1',
                '(END_GT_%d)', % self.compare_index
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

    def translate(self):
    	pass

