
import keywords
import lang
import misc

from error import ParserError


class ParserFunction:
    """Function executed at certain substring occurences while parsing."""

    def __init__(self):
        return

    def parse(self, parser, state):
        return
    pass


class PfChEscape(ParserFunction):
    def parse(self, parser, state):
        err_msg = lang.text('Parser.Error.Function.UnknownFunction')
        raise ParserError({'row': state.row, 'col': state.col - 1, 'file':
                           parser.filename, 'path': parser.filepath,
                           'cause': err_msg})
    pass


class PfChWhitespace(ParserFunction):
    def parse(self, parser, state):
        return ' '
    pass


class PfChUnescape(ParserFunction):
    def parse(self, parser, state):
        return keywords.ch_escape
    pass


class PfChComment(ParserFunction):
    def parse(self, parser, state):
        kwpos = parser.match_next_keyword(state.pos, '\n')
        comment = ''
        for i in range(state.pos, kwpos + 1):
            comment += parser.document[i]
        state.shift_forward_mul(comment)
        return ''
    pass


class PfChUncomment(ParserFunction):
    def parse(self, parser, state):
        return keywords.ch_comment
    pass


class PfScopeBegin(ParserFunction):
    def parse(self, parser, state):
        err_msg = lang.text('Parser.Error.Scope.UnexpectedBeginMarker') %\
                            keywords.scope_begin
        raise ParserError({'row': state.row, 'col': state.col - 1, 'file':
                           parser.filename, 'path': parser.filepath,
                           'cause': err_msg})
    pass


class PfScopeEnd(ParserFunction):
    def parse(self, parser, state):
        err_msg = lang.text('Parser.Error.Scope.UnexpectedEndMarker') %\
                            keywords.scope_end
        raise ParserError({'row': state.row, 'col': state.col - 1, 'file':
                           parser.filename, 'path': parser.filepath,
                           'cause': err_msg})
    pass


class PfChScopeBeginEsc(ParserFunction):
    def parse(self, parser, state):
        return keywords.scope_begin
    pass


class PfChScopeEndEsc(ParserFunction):
    def parse(self, parser, state):
        return keywords.scope_end
    pass


class PfLoadLibrary(ParserFunction):
    def parse(self, parser, state):
        m_begin = parser.match_next_keyword(keywords.scope_begin)
        if m_begin != state.pos:
            err_msg = lang.text('Parser.Error.Scope.ExpectedBeginMarker') %\
                                keywords.scope_begin
            raise ParserError({'row': state.row, 'col': state.col, 'file':
                               parser.filename, 'path': parser.filepath,
                               'cause': err_msg})
        # find end marker
        m_end = parser.match_next_keyword(keywords.scope_end)
        if m_end == -1:
            err_msg = lang.text('Parser.Error.Scope.ExpectedEndMarker') %\
                                keywords.scope_end
            state.shift_to_end(parser.document)
            raise ParserError({'row': state.row, 'col': state.col, 'file':
                               parser.filename, 'path': parser.filepath,
                               'cause': err_msg})
        # get module name
        module_name = misc.get_str_range(parser.document, m_begin + len(
                                         keywords.scope_begin), m_end - 1)
        # load module
        module_name
        # TODO: not yet implemented
        return ''
    pass
