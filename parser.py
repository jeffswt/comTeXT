
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
        self.pos = 0
        # parser stack data
        self.target = ''  # 'web' or 'doc'
        self.depth = 0  # recursion depth
        # file properties
        self.filepath = ''
        self.filename = ''
        # non-builtin macros
        self.macros = trie.Trie()
        return

    def shift_forward(self, ch):
        """Shift position markers forward at character.
        @param ch(str[0]) character at current position"""
        if ch == '\n':
            self.row += 1
            self.col = 0
        self.pos += 1
        return

    def shift_forward_mul(self, text):
        """Shift position markers forward at multiple characters.
        @param text(str) multiple characters"""
        for i in text:
            self.shift_forward(i)
        return

    def add_function(self, function_name, function):
        """Insert certain function into list.
        @param function_name(str) match string
        @param function(...) execution function"""
        self.macros[function_name] = function
        return

    def has_function(self, function_name):
        """If current scope has function, checked by its name
        @param function_name(str) match string"""
        return function_name in self.macros

    def get_function_by_name(self, function_name):
        """Get executable function by its name.
        @param function_name(str) match string"""
        return self.macros[function_name]
    pass


class Parser(object):
    """Document parser class"""

    def __init__(self, filepath, filename, document, target):
        self.filepath = filepath
        self.filename = filename
        self.headers = {}
        self.document = document
        self.target = target
        return

    def match_function(self, state, begin):
        """Find longest match of function in document.
        @param state(ParserState)
        @param begin(int) position of match begin
        @returns func(str) function name, '' if none matches"""
        p = state.macros.root
        func = ''
        cur_str = ''
        for i in range(begin, len(self.document)):
            ch = self.document[i]
            if ch not in p.children:
                break
            cur_str += ch
            p = p.children[ch]
            if p.flag is not None:
                func = cur_str
            pass
        return func

    def extract_headers(self):
        """Extract headers and generate preprocessed document."""
        lines = self.document.split('\n')
        # preproocess document headers
        self.headers = {}
        n_header_begin = 0  # first non-empty line
        n_header_end = 0  # header end
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
                err_msg = lang.text('Parser.Error.Header.Unterminated')
                raise ParserError({'row': len(lines)-1, 'col': 0, 'file':
                                   self.filename, 'path': self.filepath,
                                   'cause': err_msg})
            # process header entries
            last_header = ''
            for i in range(n_header_begin + 1, n_header_end):
                sects = lines[i].split(keywords.header_entry_separator)
                # no separator, report error
                if len(sects) <= 1:
                    err_msg = lang.text('Parser.Error.Header.EntryNoSeparator')
                    raise ParserError({'row': i, 'col': 0, 'file': self.
                                       filename, 'path': self.filepath,
                                       'cause': err_msg})
                # work on entry to form strings
                str_left = sects[0]
                str_right = keywords.header_entry_separator.join(sects[1:])
                _nl, str_left, _ = misc.split_spaces(str_left)
                _, str_right, _ = misc.split_spaces(str_right)
                # case empty index, use previous header
                if str_left == '':
                    if last_header == '':
                        err_msg = lang.text('Parser.Error.Header.NoEntryIndex')
                        raise ParserError({'row': i, 'col': 0, 'file':
                                           self.filename, 'path': self.
                                           filepath, 'cause': err_msg})
                    str_left = last_header
                    self.headers[str_left] += ' ' + str_right
                # conflicting warning
                if str_left in self.headers:
                    err_msg = lang.text('Parser.Error.Header.ConflictingIndex')
                    raise ParserError({'row': i, 'col': _nl, 'file': self.
                                       filename, 'path': self.filepath,
                                       'cause': err_msg})
                # insert into header list
                self.headers[str_left] = str_right
            # clearing header lines
            for i in range(n_header_begin, n_header_end + 1):
                lines[i] = ''
        # build dom tree
        self.document = '\n'.join(lines)
        return

    def parse_block(self, state, end_marker=None):
        """Convert document portion to a certain output format.
        @param state(ParserState) current state
        @param end_marker(str/None) terminates until this is found."""
        output = ''
        while state.pos < len(self.document):
            ch = self.document[state.pos]
            # check if end marker occured
            flag_end = True
            for i in range(state.pos, len(self.document)):
                if self.document[i] != end_marker[i - state.pos]:
                    flag_end = False
                    break
            if flag_end is True:
                state.shift_forward_mul(end_marker)
                break
            # match function
            func_name = self.match_function(state, state.pos)
            # no function matches
            if func_name == '':
                if ch != '\n':  # FIXME: should not ignore all line breaks
                    output += ch
                state.shift_forward(ch)
                continue
            else:
                state.shift_forward_mul(func_name)
            # parse function scope
            func = state.get_function_by_name(func_name)
            tmp = func.parse(self, state)
            output += tmp
        # expected end marker but none found
        if end_marker is not None and state.pos == len(self.document) - 1:
            err_msg = lang.text('Parser.Error.Scope.ExpectedEndMarker') %\
                      end_marker
            raise ParserError({'row': state.row, 'col': state.col, 'file':
                               self.filename, 'path': self.filepath,
                               'cause': err_msg})
        return

    def parse_document(self):
        """Convert document to a certain output format."""
        state = ParserState()
        # initialize parser state
        state.row = 0
        state.col = 0
        state.pos = 0
        state.target = self.target
        state.depth = 0
        state.filepath = self.filepath
        state.filename = self.filename
        # load initial functions
        # builtin special characters
        # TODO: I want to add some functions!
        state.add_function(keywords.ch_whitespace, ...)
        state.add_function(keywords.ch_unescape, ...)
        state.add_function(keywords.ch_comment, ...)
        state.add_function(keywords.ch_uncomment, ...)
        state.add_function(keywords.ch_scope_begin_esc, ...)
        state.add_function(keywords.ch_scope_end_esc, ...)
        # builtin functions
        state.add_function(keywords.kw_load_library, ...)
        state.add_function(keywords.kw_namespace, ...)
        state.add_function(keywords.kw_def_function, ...)
        state.add_function(keywords.kw_def_environment, ...)
        # call recursive parser
        self.parse_block(state)
        return
    pass
