
import re

from . import dom
from . import keywords
from . import lang
from . import misc


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
        """__init__() -- default state
        @returns None"""
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
        self.macros = {}
        return
    pass


def convert_string_to_dom(document):
    """convert_string_to_dom(document) -- convert document string to DOM
    object.
    @param document(str) a string containing the entire document
    @returns DOMObject the document DOM"""
    tree = dom.DOMObject()
    tree.append_child(dom.DOMString(document))
    return tree


def compile_document(filepath, filename, document):
    """compile_document(filepath, filename, document) -- extract headers and
    generate document DOM from document string.
    @param filepath(str) path of file
    @param filename(str) name of file
    @param document(str) document string
    @returns headers(dict(str, str)) list of headers extracted from document
    @returns tree(DOMObject) raw DOM of document, with headers removed"""
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
    tree = convert_string_to_dom('\n'.join(lines))
    return headers, tree
