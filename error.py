
class ParserError(RuntimeError):
    """Raises error while intepreting document, should be catched and displayed
    to user."""

    default_value = {
        'file': '',  # filename of error occurence
        'path': '',  # path of file
        'row': 0,  # error occured at row #0
        'col': 0,  # error occured at column #0
        'cause': '',  # reason of error
    }

    def __init__(self, cause):
        self.__parser_cause__ = cause
        return

    def cause(self):
        return self.__parser_cause__
    pass
