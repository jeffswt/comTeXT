
import jitfunction
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
        module_name = parser.match_verbatim_scope(state)
        # TODO: not yet implemented
        return module_name
    pass


class PfDefFunction(ParserFunction):
    def check_brackets(parser, state, text):
        err_msg = ''
        if not text.startswith(keywords.func_param_left):
            err_msg = lang.text('Parser.Error.Scope.'
                                'ExpectedBeginMarker') %\
                                keywords.func_param_left
        text = text[len(keywords.func_param_left):]
        if not text.endswith(keywords.func_param_right):
            err_msg = lang.text('Parser.Error.Scope.'
                                'ExpectedEndMarker') %\
                                keywords.func_param_right
        text = text[:-len(keywords.func_param_right)]
        if text.find(keywords.func_param_left) != -1:
            err_msg = lang.text('Parser.Error.Scope.'
                                'UnexpectedBeginMarker') %\
                                keywords.func_param_left
        if text.find(keywords.func_param_right) != -1:
            err_msg = lang.text('Parser.Error.Scope.'
                                'UnexpectedEndMarker') %\
                                keywords.func_param_right
        if err_msg != '':
            raise ParserError({'row': state.row, 'col': state.col - 1, 'file':
                               parser.filename, 'path': parser.filepath,
                               'cause': err_msg})
        return text.strip()

    def parse_function_def(parser, state, text):
        # get function name
        func_name, *fdm_args = text.split(keywords.func_def_marker)
        if len(fdm_args) == 0:
            err_msg = lang.text('Parser.Error.Function.MissingDefMarker')
            raise ParserError({'row': state.row, 'col': state.col, 'file':
                               parser.filename, 'path': parser.filepath,
                               'cause': err_msg})
        if len(fdm_args) > 1:
            err_msg = lang.text('Parser.Error.Function.TooManyDefMarkers')
            raise ParserError({'row': state.row, 'col': state.col +
                               len(func_name) + len(fdm_args[0]) - 1 +
                               len(keywords.func_def_marker), 'file':
                               parser.filename, 'path': parser.filepath,
                               'cause': err_msg})
        func_name = func_name.strip()
        params = list(i.strip() for i in fdm_args[0].split(
                      keywords.func_def_split))
        # parse params
        out = {
            'name': func_name,
            'lang': '',
            'args': [],  # {'name': '...', 'verbatim': True}
            'mode': ''
        }
        for param in params:
            found = False
            # language and arguments
            for l in keywords.func_lang:
                if not param.startswith(l):
                    continue
                found = True
                # already has language (conflict)?
                if out['lang'] != '':
                    err_msg = lang.text('Parser.Error.Function.'
                                        'ConflictLanguage')
                    raise ParserError({'row': state.row, 'col': state.col - 1,
                                       'file': parser.filename, 'path': parser.
                                       filepath, 'cause': err_msg})
                # check brackets
                args = param[len(l):]
                args = PfDefFunction.check_brackets(parser, state, args)
                # parse arguments
                args = list(i.strip() for i in args.split(keywords.
                            func_param_split)) if args != '' else []
                out['lang'] = l
                for arg in args:
                    verbatim = False
                    if arg.startswith(keywords.func_param_verbatim):
                        arg = arg[len(keywords.func_param_verbatim):].strip()
                        verbatim = True
                    # check argument name validity
                    for ch in keywords.func_param_forbid_chars:
                        if ch not in arg:
                            continue
                        err_msg = lang.text('Parser.Error.Function.ForbidChar')
                        raise ParserError({'row': state.row, 'col': state.col -
                                           1, 'file': parser.filename, 'path':
                                           parser. filepath, 'cause': err_msg})
                    # valid and push in
                    out['args'].append({'name': arg, 'verbatim': verbatim})
                pass
            # parse function type
            if param in keywords.func_proc:
                if out['mode'] != '':
                    err_msg = lang.text('Parser.Error.Function.ConflictMode')
                    raise ParserError({'row': state.row, 'col': state.col - 1,
                                       'file': parser.filename, 'path': parser.
                                       filepath, 'cause': err_msg})
                found = True
                out['mode'] = param
            # unknown parameter
            if not found:
                err_msg = lang.text('Parser.Error.Function.UnknownParam')
                raise ParserError({'row': state.row, 'col': state.col - 1,
                                   'file': parser.filename, 'path': parser.
                                   filepath, 'cause': err_msg})
            pass
        return out

    def parse_function(parser, state):
        # get indentation
        indent = parser.get_current_indent(state)
        # analyze function description
        func_desc = parser.match_verbatim_scope(state)
        params = PfDefFunction.parse_function_def(parser, state, func_desc)
        # enforce code block format
        if parser.match_to_next_occurence(state, '{') != '':
            err_msg = lang.text('Parser.Error.Scope.ExpectedBeginMarker')
            raise ParserError({'row': state.row, 'col': state.col, 'file':
                               parser.filename, 'path': parser.filepath,
                               'cause': err_msg})
        if parser.document[state.pos] != '\n':
            err_msg = lang.text('Parser.Error.Function.ExpectedLineBreak')
            raise ParserError({'row': state.row, 'col': state.col + 1, 'file':
                               parser.filename, 'path': parser.filepath,
                               'cause': err_msg})
        content = parser.match_to_next_occurence(state, '\n' + ' ' * indent +
                                                 keywords.scope_end)
        if len(content) > 0:
            content = content[1:]
        # checking content indentation
        lines = content.split('\n')
        min_indent = misc.get_block_indent(content)
        if min_indent <= indent:
            err_msg = lang.text('Parser.Error.Scope.Outdented') % indent
            raise ParserError({'row': state.row, 'col': state.col - 1, 'file':
                               parser.filename, 'path': parser.filepath,
                               'cause': err_msg})
        code = '\n'.join(i[min_indent:] for i in lines)
        return params, code

    def parse(self, parser, state):
        params, code = PfDefFunction.parse_function(parser, state)
        # retrieve dynamic function
        fname = keywords.kw_dyn_function % params['name']
        if state.has_function(fname):
            is_new = False
            func = state.get_function_by_name(fname)
        else:
            is_new = True
            func = PfDynamicFunction()
        # update parameters and code
        if not func.update_config(params):
            err_msg = lang.text('Parser.Error.Function.ParamMismatch')
            raise ParserError({'row': state.row, 'col': state.col - 1, 'file':
                               parser.filename, 'path': parser.filepath,
                               'cause': err_msg})
        func.update_function(parser, state, params, code)
        if is_new:
            state.add_function(fname, func)
        return ''
    pass


class PfDefEnvironment(ParserFunction):
    def parse(self, parser, state):
        params, code = PfDefFunction.parse_function(parser, state)
        # retrieve dynamic function
        fname = keywords.kw_dyn_environment_begin % params['name']
        if state.has_function(fname):
            is_new = False
            func = state.get_function_by_name(fname)
        else:
            is_new = True
            func = PfDynamicEnvironment()
        # addition limits
        if len(params['args']) == 0:
            err_msg = lang.text('Parser.Error.Environment.TooFewArgs')
            raise ParserError({'row': state.row, 'col': state.col - 1, 'file':
                               parser.filename, 'path': parser.filepath,
                               'cause': err_msg})
        if not params['args'][-1]['verbatim']:
            err_msg = lang.text('Parser.Error.Environment.LastMustVerbatim')
            raise ParserError({'row': state.row, 'col': state.col - 1, 'file':
                               parser.filename, 'path': parser.filepath,
                               'cause': err_msg})
        # update parameters and code
        if not func.update_config(params):
            err_msg = lang.text('Parser.Error.Function.ParamMismatch')
            raise ParserError({'row': state.row, 'col': state.col - 1, 'file':
                               parser.filename, 'path': parser.filepath,
                               'cause': err_msg})
        func.update_function(parser, state, params, code)
        if is_new:
            state.add_function(fname, func)
        return ''
    pass


class PfEnvironmentBegin(ParserFunction):
    def parse(self, parser, state):
        err_msg = lang.text('Parser.Error.Environment.UnknownEnvironment')
        raise ParserError({'row': state.row, 'col': state.col, 'file':
                           parser.filename, 'path': parser.filepath,
                           'cause': err_msg})
    pass


class PfEnvironmentEnd(ParserFunction):
    def parse(self, parser, state):
        err_msg = lang.text('Parser.Error.Scope.UnexpectedEndMarker') %\
                            keywords.kw_environment_end
        raise ParserError({'row': state.row, 'col': state.col - 1, 'file':
                           parser.filename, 'path': parser.filepath,
                           'cause': err_msg})
    pass


class PfDynamicFunction(ParserFunction):
    def __init__(self):
        self.function_name = None
        self.args_vb = None  # verbatim parse or not
        self.mode = None
        self.py_func = None
        self.raw_func = None
        return

    def update_config(self, params):
        """Update configuration of current function. Newly updated parameters
        must be the same as the original.
        @param params(dict(...)) taken from PfDefFunction
        @returns bool True if modification succeeded"""
        if self.function_name is not None:
            if self.function_name != params['name']:
                return False
            if len(self.args_vb) != len(params['args']):
                return False
            for i in range(0, len(self.args_vb)):
                if self.args_vb[i] != params['args']['verbatim']:
                    return False
            if self.mode != params['mode']:
                return False
            return True
        self.function_name = params['name']
        self.args_vb = list(i['verbatim'] for i in params['args'])
        self.mode = params['mode']
        return True

    def update_function(self, parser, state, params, code):
        fname = params['name']
        args = list(i['name'] for i in params['args'])
        if params['lang'] == keywords.func_lang_py:
            if self.py_func is not None:
                err_msg = lang.text('Parser.Error.Function.ConflictCode')
                raise ParserError({'row': state.row, 'col': state.col - 1,
                                   'file': parser.filename, 'path': parser.
                                   filepath, 'cause': err_msg})
            self.py_func = jitfunction.JitFunctionPy(fname, args, code)
        elif params['lang'] == keywords.func_lang_raw:
            if self.raw_func is not None:
                err_msg = lang.text('Parser.Error.Function.ConflictCode')
                raise ParserError({'row': state.row, 'col': state.col - 1,
                                   'file': parser.filename, 'path': parser.
                                   filepath, 'cause': err_msg})
            self.raw_func = jitfunction.JitFunctionRaw(fname, args, code)
        return

    def parse(self, parser, state):
        args = []
        for verbatim in self.args_vb:
            if verbatim:
                args.append(parser.match_verbatim_scope(state))
            else:
                args.append(parser.match_parsable_scope(state))
        # call function
        res = ''
        if self.raw_func is not None:
            res = str(self.raw_func.eval(*args))
        elif self.py_func is not None:
            res = str(self.py_func.eval(*args))
        return res
    pass


class PfDynamicEnvironment(ParserFunction):
    def __init__(self):
        self.function_name = None
        self.args_vb = None  # verbatim parse or not
        self.mode = None
        self.py_func = None
        self.raw_func = None
        return

    def update_config(self, params):
        return PfDynamicFunction.update_config(self, params)

    def update_function(self, parser, state, params, code):
        return PfDynamicFunction.update_function(self, parser, state,
                                                 params, code)

    def parse(self, parser, state):
        args = []
        indent = parser.get_current_indent(state)
        for verbatim in self.args_vb[:-1]:
            if verbatim:
                args.append(parser.match_verbatim_scope(state))
            else:
                args.append(parser.match_parsable_scope(state))
        if parser.document[state.pos] != '\n':
            err_msg = lang.text('Parser.Error.Environment.ExpectedLineBreak')
            raise ParserError({'row': state.row, 'col': state.col - 1,
                               'file': parser.filename, 'path': parser.
                               filepath, 'cause': err_msg})
        state.shift_forward('\n')
        fn_end = keywords.kw_dyn_environment_end % self.function_name
        args.append(parser.match_to_next_occurence(state, '\n' + ' ' * indent +
                    fn_end, sub_display_error=fn_end))
        # call function
        res = ''
        if self.raw_func is not None:
            res = str(self.raw_func.eval(*args))
        elif self.py_func is not None:
            res = str(self.py_func.eval(*args))
        return res
    pass
