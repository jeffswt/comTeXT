
import re

from . import keywords
from . import lang
from . import misc
from . import trie


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


class ParserState(object):
    """Stores the current state of the parser."""

    def __init__(self):
        # location definition
        self.row = 0
        self.col = 0
        # parser stack data
        self.depth = 0  # recursion depth
        self.end_marker = None
        # file properties
        self.filename = ''
        self.filepath = ''
        # non-builtin macros
        self.macros = trie.Trie()
        return
    pass


def compile_document(filepath, filename, document):
    """Extract headers and generate preprocessed document.
    @param filepath(str) path of file
    @param filename(str) name of file
    @param document(str) document string
    @returns headers(dict(str, str)) list of headers extracted from document
    @returns document(str) document with headers removed"""
    lines = document.split('\n')
    # preproocess document headers
    n_header_begin = 0  # first non-empty line
    n_header_end = 0  # header end
    headers = {}  # dict of strings representing header entries
    for i in range(0, len(lines)):
        if len(re.sub(r' +$', r'', lines[i])) > 0:
            break
        n_header_begin += 1
    # process header if exists
    if lines[n_header_begin].startswith(keywords.header_marker_begin):
        # locate header end
        for i in range(n_header_begin + 1, len(lines)):
            if lines[i].startswith(keywords.header_marker_end):
                n_header_end = i
                break
        # if header end does not exists, report error
        if n_header_end == 0:
            raise ParserError({'row': len(lines)-1, 'col': 0, 'file': filename,
                               'path': filepath, 'cause': lang.text(
                               'Parser.Error.Header.Unterminated')})
        # process header entries
        last_header = ''
        for i in range(n_header_begin + 1, n_header_end):
            sects = lines[i].split(keywords.header_entry_separator)
            # no separator, report error
            if len(sects) <= 1:
                err_msg = lang.text('Parser.Error.Header.EntryNoSeparator')
                raise ParserError({'row': i, 'col': 0, 'file': filename,
                                   'path': filepath, 'cause': err_msg})
            # work on entry to form strings
            str_left = sects[0]
            str_right = keywords.header_entry_separator.join(sects[1:])
            _nl, str_left, _ = misc.split_spaces(str_left)
            _, str_right, _ = misc.split_spaces(str_right)
            # case empty index, use previous header
            if str_left == '':
                if last_header == '':
                    err_msg = lang.text('Parser.Error.Header.NoEntryIndex')
                    raise ParserError({'row': i, 'col': 0, 'file': filename,
                                       'path': filepath, 'cause': err_msg})
                str_left = last_header
                headers[str_left] += ' ' + str_right
            # conflicting warning
            if str_left in headers:
                err_msg = lang.text('Parser.Error.Header.ConflictingIndex')
                raise ParserError({'row': i, 'col': _nl, 'file': filename,
                                   'path': filepath, 'cause': err_msg})
            # insert into header list
            headers[str_left] = str_right
        # clearing header lines
        for i in range(n_header_begin, n_header_end + 1):
            lines[i] = ''
    # build dom tree
    return headers, '\n'.join(lines)


def parse_document(headers, document, target):
    """Convert document to a certain output format.
    @param headers(dict(str, str)) headers
    @param document(str) document string
    @param target(str) 'web' or 'doc'
    @returns document(str) converted document"""

    return
