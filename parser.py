
import re

import keywords
import lang
import misc
import trie
import modules

from error import ParserError


class ParserState:
    """Stores the current state of the parser."""

    def __init__(self):
        # location definition
        self.row = 0
        self.col = 0
        self.pos = 0
        # parser stack data
        self.target = ''  # 'web' or 'doc'
        self.depth = 0  # recursion depth
        self.exec_count = 0  # executed function count
        self.autobreak = misc.DictObject(
            opened=False,
            space=False,
            breaks=False,
            m_b=False,
            m_e=False
        )
        # file properties
        self.filepath = ''
        self.filename = ''
        # non-builtin macros
        self.macros = trie.Trie()
        return

    def shift_forward(self, ch):
        """Shift position markers forward at character.
        @param ch(str[0]) character at current position"""
        self.col += 1
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

    def shift_to_end(self):
        """Shift to document end.
        @param text(str) entire document"""
        begin = self.pos
        text = self.document
        for i in range(begin, len(text)):
            self.shift_forward(text[i])
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


class Parser:
    """Document parser class"""

    def __init__(self, filepath, filename, document, target):
        self.filepath = filepath
        self.filename = filename
        self.headers = {}
        self.document = document
        self.source = document  # original, unmodified document
        self.target = target
        return

    def get_current_indent(self, state):
        """Get the indentation for current line, in spaces.
        @param state(ParserState)
        @returns indent(int)"""
        indent = 0
        for _ in range(state.pos, -1, -1):
            ch = state.document[state.pos]
            if ch == '\n':
                break
            elif ch == ' ':
                indent += 1
            else:
                indent = 0
        return indent

    def process_auto_break(self, state, ch, nobreak=False, dospace=False):
        """Auto break utility, returns inserted string (buffer)."""
        ab = state.autobreak
        if ch == ' ':
            if not ab.opened:
                return ''
            if ab.breaks > 0:
                return ''
            ab.space = True
            return ''
        elif ch == '\n':
            if not ab.opened:
                return ''
            ab.space = True
            ab.breaks += 1
            return ''
        # process normal case
        if not ab.opened:
            if nobreak and not dospace:
                return ch
            ab.opened = True
            return ab.m_b + ch
        if ab.space:
            ab.space = False
            if ab.breaks < 2:
                ab.breaks = 0
                return ' ' + ch
            elif nobreak:
                return ' ' + ch
        if ab.breaks > 0:
            if nobreak:
                return ch
            s = min(ab.breaks // 2, 1)  # no more than 1 paragraph break
            ab.breaks = 0
            return (ab.m_e + ab.m_b) * s + ch
        return ch

    def close_auto_break(self, state):
        ab = state.autobreak
        if not ab.opened:
            return ''
        ab.opened = False
        ab.space = False
        ab.breaks = 0
        return ab.m_e

    def match_function(self, state, begin):
        """Find longest match of function in document.
        @param state(ParserState)
        @param begin(int) position of match begin
        @returns func(str) function name, '' if none matches"""
        p = state.macros.root
        func = ''
        cur_str = ''
        for i in range(begin, len(state.document)):
            ch = state.document[i]
            if ch not in p.children:
                break
            cur_str += ch
            p = p.children[ch]
            if p.flag is not None:
                func = cur_str
            pass
        return func

    def match_next_keyword(self, state, begin, sub):
        """Match position of next occurence of sub starting from begin.
        @param begin(int)
        @param sub(str)
        @returns res(int) -1 if failure"""
        return state.document.find(sub, begin)

    def match_to_next_occurence(self, state, sub, sub_display_error=None):
        """Match until next occurence of ...sub.
        @param state(ParserState)
        @returns res(str) inner contents"""
        pos = self.match_next_keyword(state, state.pos, sub)
        if pos == -1:
            if sub_display_error is not None:
                sub = sub_display_error
            err_msg = lang.text('Parser.Error.Scope.ExpectedEndMarker') % sub
            state.shift_to_end()
            raise ParserError({'row': state.row, 'col': state.col, 'file':
                               state.filename, 'path': state.filepath,
                               'cause': err_msg})
        res = misc.get_str_range(state.document, state.pos, pos - 1)
        state.shift_forward_mul(res + sub)
        return res

    def match_verbatim_scope(self, state):
        """Match immediate {...} and return contents.
        @param state(ParserState)"""
        m_begin = self.match_next_keyword(state, state.pos,
                                          keywords.scope_begin)
        if m_begin != state.pos:
            err_msg = lang.text('Parser.Error.Scope.ExpectedBeginMarker') %\
                                keywords.scope_begin
            raise ParserError({'row': state.row, 'col': state.col, 'file':
                               state.filename, 'path': state.filepath,
                               'cause': err_msg})
        state.shift_forward_mul(keywords.scope_begin)
        return self.match_to_next_occurence(state, keywords.scope_end)

    def match_parsable_scope(self, state, do_space=True):
        """Match {...} and return parsed contents.
        @param state(ParserState)"""
        m_begin = self.match_next_keyword(state, state.pos,
                                          keywords.scope_begin)
        if m_begin != state.pos:
            err_msg = lang.text('Parser.Error.Scope.ExpectedBeginMarker') %\
                                keywords.scope_begin
            raise ParserError({'row': state.row, 'col': state.col, 'file':
                               state.filename, 'path': state.filepath,
                               'cause': err_msg})
        state.shift_forward_mul(keywords.scope_begin)
        state.depth += 1
        res = self.parse_block(state, end_marker=keywords.scope_end,
                               do_space=do_space)
        state.depth -= 1
        return res

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
                    self.headers[last_header] += ' ' + str_right
                # conflicting warning
                if str_left in self.headers:
                    err_msg = lang.text('Parser.Error.Header.ConflictingIndex')
                    raise ParserError({'row': i, 'col': _nl, 'file': self.
                                       filename, 'path': self.filepath,
                                       'cause': err_msg})
                # insert into header list
                last_header = str_left
                self.headers[str_left] = str_right
            # clearing header lines
            for i in range(n_header_begin, n_header_end + 1):
                lines[i] = ''
        # build dom tree
        self.document = '\n'.join(lines)
        return

    def parse_block(self, state, end_marker=None, auto_break=False,
                    do_space=True):
        """Convert document portion to a certain output format.
        @param state(ParserState) current state
        @param end_marker(str/None) terminates until this is found."""
        output = ''
        while state.pos < len(state.document):
            ch = state.document[state.pos]
            # check if end marker occured, only if there is an end marker
            if end_marker is not None:
                flag_end = True
                for i in range(state.pos, min(len(state.document),
                               state.pos + len(end_marker))):
                    if state.document[i] != end_marker[i - state.pos]:
                        flag_end = False
                        break
                if flag_end is True:
                    state.shift_forward_mul(end_marker)
                    break
            # match function
            func_name = self.match_function(state, state.pos)
            # no function matches
            if func_name == '':
                if state.depth == 0 or auto_break:
                    output += self.process_auto_break(state, ch,
                                                      dospace=do_space)
                else:
                    output += self.process_auto_break(state, ch, nobreak=True,
                                                      dospace=do_space)
                state.shift_forward(ch)
                continue
            else:
                state.shift_forward_mul(func_name)
            # parse function scope
            func = state.get_function_by_name(func_name)
            state.depth += 1
            tmp = func.parse(self, state)
            state.depth -= 1
            state.exec_count += 1
            output += tmp
        # expected end marker but none found
        if end_marker is not None and state.pos == len(state.document) - 1:
            err_msg = lang.text('Parser.Error.Scope.ExpectedEndMarker') %\
                      end_marker
            raise ParserError({'row': state.row, 'col': state.col, 'file':
                               state.filename, 'path': state.filepath,
                               'cause': err_msg})
        # finally
        return output

    def parse_blob(self, state, blob):
        """Completely eradicate all functions in scope."""
        while True:
            ns = self.create_parser_state(state.target, functions=state.macros,
                                          document=blob)
            bec = ns.exec_count
            blob = self.parse_document(ns)
            state.macros = ns.macros
            if bec == ns.exec_count:
                break
        return blob

    def create_parser_state(self, target, document=None, functions=None):
        """Create initial parser state for parsing."""
        state = ParserState()
        # initialize basic parameters
        state.row = 0
        state.col = 0
        state.pos = 0
        state.target = target
        state.depth = 0
        state.autobreak.m_b = {
            'doc': keywords.autobrk_para_begin_doc,
            'web': keywords.autobrk_para_begin_web,
            'ctx': '',
        }.get(state.target, '')
        state.autobreak.m_e = {
            'doc': keywords.autobrk_para_end_doc,
            'web': keywords.autobrk_para_end_web,
            'ctx': '',
        }.get(state.target, '')
        state.filepath = self.filepath
        state.filename = self.filename
        # load initial functions
        if functions is None:
            state.add_function(keywords.ch_escape, modules.PfChEscape())
            state.add_function(keywords.ch_whitespace,
                               modules.PfChWhitespace())
            state.add_function(keywords.ch_unescape, modules.PfChUnescape())
            state.add_function(keywords.ch_comment, modules.PfChComment())
            state.add_function(keywords.ch_uncomment, modules.PfChUncomment())
            state.add_function(keywords.scope_begin, modules.PfScopeBegin())
            state.add_function(keywords.scope_end, modules.PfScopeEnd())
            state.add_function(keywords.ch_scope_begin_esc,
                               modules.PfChScopeBeginEsc())
            state.add_function(keywords.ch_scope_end_esc,
                               modules.PfChScopeEndEsc())
            state.add_function(keywords.kw_load_library,
                               modules.PfLoadLibrary())
            state.add_function(keywords.kw_def_function,
                               modules.PfDefFunction())
            state.add_function(keywords.kw_def_environment,
                               modules.PfDefEnvironment())
            state.add_function(keywords.kw_environment_begin,
                               modules.PfEnvironmentBegin())
            state.add_function(keywords.kw_environment_end,
                               modules.PfEnvironmentEnd())
            state.add_function(keywords.kw_paragraph,
                               modules.PfParagraph())
        else:
            for i in functions:
                state.add_function(i, functions[i])
        # load document
        if document is None:
            state.document = self.document
        else:
            state.document = document
        return state

    def parse_document(self, state):
        """Convert arbitrary document to a certain output format."""
        # preprocess document
        d = self.parse_block(state)
        d += self.close_auto_break(state)
        return state, d

    def parse(self):
        """Parse this certain document."""
        try:
            self.extract_headers()
            state = self.create_parser_state('ctx', document=self.document)
            self.document = self.parse_document(state)
            state = self.create_parser_state(self.target, self.document,
                                             functions=state.macros)
            self.document = self.parse_document(state)
            return self.document
        except ParserError as err:
            raise err
            # cause = err.cause()
            # lines = self.source.split('\n')
            # err_res = '%s:%d:%d: error: %s\n%s\n%s^' %\
            #           (cause['file'], cause['row'] + 1, cause['col'] + 1,
            #            cause['cause'], lines[cause['row']],
            #            ' ' * cause['col'])
            # print(err_res, end='')
        return ''
    pass


f = open('test.tex', 'r', encoding='utf8')
s = f.read()
f.close()

p = Parser('.', 'test.tex', s, 'web')
r = p.parse()

print(r)
