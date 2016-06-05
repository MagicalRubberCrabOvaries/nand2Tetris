#! python3


class SymbolTable(object):
    """Creates an object which stores symbols which correspond to RAM slots"""

    def __init__(self):

        self.SP = 0
        self.LCL = 1
        self.ARG = 2
        self.THIS = 3
        self.THAT = 4
        self.SCREEN = 16384
        self.KBD = 24576

        for i in range(16):
            self['R%d' % i] = i

    def __str__(self):
        return "{}".format(self.__class__.__name__)
        # string = ''
        # for key, value in self.__iter__():
        #     string += '{}: {}\n'.format(key, value)
        # return string

    # attribute/item dunders
    def __getitem__(self, key):
        """grabs the attribute by key"""
        return self.__dict__.get(key, None)

    def __setitem__(self, key, value):
        """sets attribute key by value"""
        if key not in self.__dict__:
            self.__dict__[key] = value

    def __delitem__(self, key):
        """delete the attribute by key"""
        if key in self.__dict__:
            del self.__dict__[key]

    # iterable dunders
    def __iter__(self):
        """Iterates over data within the SymbolTable"""
        for key, value in self.__dict__.items():
            yield key, value

    def __contains__(self, key):
        """checks self for key"""
        return key in self.__dict__
