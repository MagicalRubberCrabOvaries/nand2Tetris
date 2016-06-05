#! python 3

import jack
import os
import sys
import logging

class Assembler(object):
    """Loads a .asm file and translates it into Hack Machine Code"""

    def __init__(self, filepath):

        # Init logger object first.

        # Create Logger with "Assembler"
        self.logger = logging.getLogger("Assembler")
        self.logger.setLevel(logging.DEBUG)
        # File handler which logs even debug messages.
        fh = logging.FileHandler('Assembler.log')
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
        
        # With logger object, announce that an Assembler has been initialized.
        self.logger.debug("Assembler initialized {}".format(filepath))

        # Store filepath for use and init empty list for binary instructions.
        self.filepath = os.path.abspath(filepath)
        self.binary = []

    def __str__(self):
        return self.__class__.__name__
        # self.logger.debug("Printing Assembler's binary")
        # string = ''
        # for line in self:
        #     string += line + '\n'
        # return string

    def __repr__(self):

        return "<{}: {}>".format(self.__class__.__name__, self.binary[-1])

    def __iter__(self):

        self.logger.debug("Iterating over {}".format(self.__class__.__name__))
        binary = self.binary
        for line in binary:
            yield line[:line.find('\n')]

    def assemble(self):
        """Take file and parse into machine code"""

        self.logger.info(
            "{} assembling {}".format(
                self.__class__.__name__, self.filepath
            )
        )

        self.logger.info("Initializing parser, symbol, and code modules")

        # set up assembler components.
        Parser = jack.AssemblyParser(self.filepath, isFile=True)
        CodeWriter = jack.AssemblyCode()
        SymbolTable = jack.SymbolTable()

        linenum = 0  # ROM line number.
        sysmem = 16  # var storage begins at register 16.

        self.logger.info("{} itterating over {}".format(self, Parser))

        # __iter__ in Parser returns everything it can possibly parse each loop
        for command, commandType, symbol, dest, comp, jump in Parser:

            self.logger.info(
                "{} itteration: {}: {} (Sym: {} D: {}, C: {}, J: {})".format(
                    linenum, command, commandType, symbol, dest, comp, jump
                )
            )

            if commandType == Parser.L_COMMAND:

                self.logger.debug(
                    "Storing {} as {} in {}".format(
                        symbol, linenum, SymbolTable
                    )
                )
                # Store the label's line number but DO NOT increase
                # linenum var. L commands are not stored in ROM.
                SymbolTable[symbol] = linenum
                continue

            elif commandType == Parser.A_COMMAND:

                if not symbol.isnumeric():
                    # If A command has a symbol for an address
                    label = '(%s)' % symbol
                    if symbol not in SymbolTable and label in Parser:
                        # Search for a label version of the symbol in future
                        # commands if it does not exist in SymbolTable if such
                        # a label exists in the Assembly code.

                        self.logger.info(
                            "{} searching for {} in {}".format(
                                Assembler, label, Parser
                            )
                        )

                        num = Parser.search(label)
                        SymbolTable[symbol] = num

                        self.logger.info(
                            "Storing {} as {} in {}".format(
                                symbol, num, SymbolTable
                            )
                        )

                    elif symbol not in SymbolTable:
                        # If A command's symbol does not exist as a label and
                        # has not been stored in Symbol table, store it.

                        self.logger.info(
                            "Storing {} as {} in {}".format(
                                symbol, sysmem, SymbolTable
                            )
                        )

                        SymbolTable[symbol] = sysmem
                        sysmem += 1  # Increment sysmem to next register.

                    address = SymbolTable[symbol]

                    self.logger.info(
                        "Retrieving address from {}.".format(SymbolTable)
                    )

                else:
                    address = symbol

                self.logger.info("Address: {}".format(address))

                # Convert to binary string.
                address = bin(int(address))[2:]

                # lengthen to 15 bits
                address = '0' * (15 - len(address)) + address
                self.binary.append('0%s\n' % address)

                self.logger.warn("Writing A command: {}".format(self.binary[-1]))

            else:  # C command is the only other possibility.
                abit = '1' if 'M' in Parser.comp() else '0'
                self.binary.append(
                    '111%s%s%s%s\n' % (
                        abit,
                        CodeWriter.comp(comp),
                        CodeWriter.dest(dest),
                        CodeWriter.jump(jump)
                    )
                )
                self.logger.warn("Writing C command: {}".format(self.binary[-1]))

            linenum += 1

    def saveFile(self):
        """Writes self.binary to a .bin file."""

        newfilepath = self.filepath[:self.filepath.find('.asm')] + '.hack'
        with open(newfilepath, 'w') as binaryFile:
                binaryFile.writelines(self.binary)
                binaryFile.close()

if __name__ == '__main__':

    while True:

        try:
            print("Enter filepath. Relative paths to the cwd are acceptable.")
            filepath = input()
            if not os.path.exists(filepath) or not filepath.endswith('.asm'):
                raise IOError

            A = Assembler(filepath)

        except IOError:
            print("IOError. Enter real filepath ending in .asm")
            continue

        break

    A.assemble()
    A.saveFile()
    print("Done")
    sys.exit()
    quit()
