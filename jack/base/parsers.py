#! python3

# Parsers module contains parser objects for Hack Assembly,
# Jack  Virtual Machine, and Jack Compiler.

import os
import re

class BaseParser(object):
    """Parent class for all parsers"""

    def __init__(self, filepath):

        self.filepath = os.path.abspath(filepath)
        self.name = os.path.basename(filepath[:filepath.find('.')])
        srcFile = open(filepath, 'r')
        rawText = srcFile.readlines()
        srcFile.close()

        lines = []
        commented = False
        for line in rawText:
            if commented:
                if '*/' in line:
                    commented = False
                else:
                    continue

            elif line.startswith('/*') and not commented:
                commented = True

            elif '/*' in line:
                lines.append(line[:line.find('/*')].strip())
                commented = True

            elif line not in ('', '\n') and not line.startswith('//'):
                lines.append(line[:line.find('//')].strip())

        self.lines = lines
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

    def __repr__(self):
 
        return "<{}: {}>".format(self.__class__.__name__, self.command)

    def __iter__(self):
        for line in self.lines:
            yield line

    def __contains__(self, key):
        """return boolean if key is in any line in code"""
        lines = '\n'.join(self.lines)
        return key in lines

    def __len__(self):
        """return length of list of lines at self.lines"""
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

    def hasMoreCommands(self):
        """Returns a boolean of whether the parser has reached the last line"""
        return not self.curr_line == self.end_line

    def advance(self):
        """Points to the current index of the commands."""
        if self.hasMoreCommands():
            self.curr_line += 1
            self.command = self.lines[self.curr_line]
        else:
            return None

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

    # Constants
    A_COMMAND = 'A_COMMAND'
    C_COMMAND = 'C_COMMAND'
    L_COMMAND = 'L_COMMAND'

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


class VMParser(BaseParser):

    C_ARITHMETIC = 'C_ARITHMETIC'
    C_PUSH = 'C_PUSH'
    C_POP = 'C_POP'
    C_LABEL = 'C_LABEL'
    C_GOTO = 'C_GOTO'
    C_IF = 'C_IF'
    C_FUNCTION = 'C_FUNCTION'
    C_RETURN = 'C_RETURN'
    C_CALL = 'C_CALL'

    def __iter__(self):
        self.reset()
        for i in range(len(self)):
            yield(
                self.command,
                self.commandType(),
                self.arg1(),
                self.arg2()
            )
            self.advance()
        self.reset()

    def commandType(self):
        
        for i in (
            'add', 'sub', 'neg', 
            'eq', 'gt', 'lt', 
            'and', 'or', 'not'
        ):
            if i in self.command:
                return self.C_ARITHMETIC

        arg = self.command[:self.command.find(' ')]

        if arg == 'pop':
            return self.C_POP
        elif arg == 'push':
            return self.C_PUSH
        elif arg == 'label':
            return self.C_LABEL
        elif arg == 'function':
            return self.C_FUNCTION
        elif arg == 'goto':
            return self.C_GOTO
        elif arg == 'if-goto':
            return self.C_IF
        elif arg == 'call':
            return self.C_CALL
        else: # arg == 'return':
            return self.C_RETURN

    def arg1(self):
        """Returns string portion of arg"""
        c_type = self.commandType()
        if c_type == self.C_ARITHMETIC:
            return self.command
        elif c_type == self.C_RETURN:
            return None
        else:
            return self.command.split()[1]

    def arg2(self):
        """Returns int portion of arg"""
        if self.commandType() in (
            self.C_PUSH, self.C_POP, self.C_CALL, self.C_FUNCTION
        ):
            return int(self.command.split()[-1])
        else:
            None


class JackTokenizer(BaseParser):

    # Scanner osbject 
    tokenRe = re.compile(r"""
        (//.*\n)                    # 0. comment to end of line.
        |(/[*]{1,2}[*]/)          # 1. comment until end comment.
                                    # 2. keyword
        |(class|function|constructor|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)
        |([{}\[\]().,;|~&+-/*=<>])  # 3. symbol
        |(\d+)                      # 4. int constant
        |(\".*\")                   # 5. str constant
        |(\w+[_0-9A-Za-z]*)         # 6. identifier
        """, re.VERBOSE | re.DOTALL)

    # Constants
    KEYWORD = 'KEYWORD'
    SYMBOL = 'SYMBOL'
    INT_CONST = 'INT_CONST'
    STRING_CONST = 'STRING_CONST'
    IDENTIFIER = 'IDENTIFIER'
    # Indeces:                 2.|     3.|        4.|           5.|         6.
    TYPES = (None, None, KEYWORD, SYMBOL, INT_CONST, STRING_CONST, IDENTIFIER)

    def __init__(self, filepath):
        """This class has a different init from other parsers because
        of the needs of tokenizing with a regex. Still, the tokens list
        is stored in the 'lines' attribute (self.lines) for inherited 
        methods.
        """

        self.filepath = os.path.abspath(filepath)
        self.name = os.path.basename(filepath[:filepath.find('.')])
        
        srcFile = open(filepath, 'r')
        code = srcFile.read()
        srcFile.close()

        tokens = self.tokenRe.findall(code)
        tokenlist = []
        for token in tokens:
            for i in range(2, 7):
                if token[i] == '':
                    continue
                else:
                    tokenlist.append((i, token[i]))
                    break

        self.lines = tokenlist
        self.curr_line = 0
        self.end_line = len(self.lines) - 1
        self.command = self.lines[self.curr_line]

    def __iter__(self):
        self.reset()
        for i in range(len(self)):
            ttype = self.tokenType()
            yield(
                ttype,
                self.getToken(ttype)
            )
            self.advance()
        self.reset()
            
    def tokenType(self):
        """Access current token tuple.
        First entry is token_id.
        return lexical constant matching id.

        id is the same as the index in TYPES
        """
        return self.TYPES[self.command[0]]

    def getToken(self, ttype=None):

        if ttype == None:
            # If no input, get type.
            ttype = self.tokenType()
        
        if ttype in (self.KEYWORD, self.IDENTIFIER, self.SYMBOL):
            # return token
            return self.command[1]
        elif ttype == self.INT_CONST:
            # return token as int.
            return int(self.command[1])
        elif ttype == self.STRING_CONST:
            # return token excluding double quotes (")
            return self.command[1][1:-1]
        else:
            # Invalid type.
            return None
