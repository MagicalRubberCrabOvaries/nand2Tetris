#! python3

# Parsers module contains parser objects for Hack Assembly,
# Jack  Virtual Machine, and Jack Compiler.


class BaseParser(object):
    """Parent class for all parsers"""

    def __init__(self, code, isFile=False):

        if isFile:
            self.loadFile(code)
        else:
            self.lines = code

        self.curr_line = 0
        self.end_line = len(self.lines) - 1
        self.command = self.lines[self.curr_line]

    def __str__(self):
        return "{}: {}, {} of {}".format(
            self.__class__.__name__,
            self.command,
            self.curr_line,
            self.end_line
        )
        # string = ''
        # for line in self.lines:
        #     string += line + '\n'
        # return string

    def __repr__(self):
 
        return "<{}: {}>".format(self.__class__.__name__, self.command)

    def __iter__(self):
        linenum = 0
        for line in self.lines:
            yield linenum, line
            linenum += 1

    def __contains__(self, key):

        lines = '\n'.join(self.lines)
        return key in lines

    def __len__(self):
        
        return len(self.lines)

    def search(self, keyw):
        
        if keyw in self:

            linenum = 0
            for line in self.lines:
                
                if keyw in line:
                    return linenum        
                elif line.startswith('(') and line.endswith(')'):
                    continue
                else:
                    linenum += 1
        
        else:
            return None

    def loadFile(self, filepath):
        """Loads a file, strips it of whitespace,
         and stores lines as an array."""

        with open(filepath) as srcFile:
            rawText = srcFile.readlines()
            srcFile.close()

        lines = []
        for line in rawText:
            if line not in ('', '\n') and not line.startswith('//'):
                lines.append(line[:line.find('//')].strip())

        self.lines = lines

    def hasMoreCommands(self):
        """Returns a boolean of whether the parser has reached the last line"""
        return not self.curr_line == self.end_line

    def advance(self):
        """Points to the current index of the commands."""
        self.curr_line += 1
        self.command = self.lines[self.curr_line]

    def reset(self):
        """Sets pointer back to top of command array"""
        self.curr_line = 0


class AssemblyParser(BaseParser):

    # Hack assembly language specification
    # ---A command---
    # @<number/symbol>
    # Usage - sets A register which contains current address to <number/symbol>
    #
    # ---C command---
    # <dest>=<comp>;<jump>
    # Computes artithmetic, stores results, and issues jump commands if
    # provided
    #
    # ---L pseudo-command ---
    # (LABEL)
    # Creates markers for jump points in symbol table.
    # This pseudo-command only affects the assembler and not the hardware.

    def __init__(self, asm, isFile=False):

        super(AssemblyParser, self).__init__(asm, isFile=isFile)
        self.A_COMMAND = 'A_COMMAND'
        self.C_COMMAND = 'C_COMMAND'
        self.L_COMMAND = 'L_COMMAND'

    def __iter__(self):

        self.reset()
        for i in range(len(self)):

            yield (
                self.command,
                self.commandType(),
                self.symbol(),
                self.dest(),
                self.comp(),
                self.jump()
            )

            if self.hasMoreCommands():
                self.advance()
        self.reset()


    def commandType(self):
        """ Returns the type of Assembly command the current line is"""

        if self.command.startswith('(') and self.command.endswith(')'):
            return self.L_COMMAND
        elif self.command.startswith('@'):
            return self.A_COMMAND
        else:
            return self.C_COMMAND

    def symbol(self):
        """Isolates the symbol of the current line if L or A command."""
        commandType = self.commandType()
        if commandType == self.L_COMMAND:
            return self.command[1:-1]
        elif commandType == self.A_COMMAND:
            return self.command[1:]
        else:
            return None

    def dest(self):
        """Returns destination component of C command"""
        return self.command[:self.command.find('=')] \
            if '=' in self.command else None

    def comp(self):
        """Returns computation component of C command"""
        command = self.command
        if '=' in command:
            command = command[command.find('=') + 1:]
        if ';' in command:
            command = command[:command.find(';')]

        return command

    def jump(self):
        """Returns jump component of C command"""
        return self.command[self.command.find(';') + 1:] \
            if ';' in self.command else None

# class MacroParser(BaseParser):

#    # ---J macro ---
#    # <jump> <address num/symbol>
#    # A macro of an A command followed by a C command D;<jump>
#    # If <jump> is JMP, then the C command is instead 0;JMP
#    #
#    # ---M macro ---
#    # A?M[address]?D?=<comp>;<jump>
#    # <dest>=M[address]in<comp>;<jump>
#    #
#    # A macro of an A command and a C command that utilizes the contents of
#    # that ram address.
#    #
#    # ---M2 macro---
#    # A?M[address]D?=M[i];<jump>
#    # <dest>=M[address]+M[address2];<jump>
#    # Macro of 2 M macros
#    #
#    # ---M3 macro---
#    # A?M[address]?D?=M[address2]+M[address3];<jump>
#    # Macro of 3 M macros.

#    def __init__(self, code, isFile=False):

#        super().__init__(code, isFile)
#        # Macro of an A and C command.
#        self.M_MACRO   = 'M_MACRO'
#        # Macro of an A and D;<jump mnem> C command.
#        self.J_MACRO   = 'J_MACRO'

#       self.M2_MACRO  = 'M2_MACRO' # Macro of 2 M macros.
#       self.M3_MACRO  = 'M3_MACRO' # Macro of 3 M macros.

