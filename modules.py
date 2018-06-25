
import os

import jitfunction
import keywords
import lang
import misc
import kernel

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
        print(list(state.macros))
        err_msg = lang.text('Parser.Error.Function.UnknownFunction')
        raise ParserError({'row': state.row, 'col': state.col - 1, 'file':
                           state.filename, 'path': state.filepath,
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
        kwpos = parser.match_next_keyword(state, state.pos, '\n')
        comment = ''
        for i in range(state.pos, kwpos + 1):
            comment += state.document[i]
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
                           state.filename, 'path': state.filepath,
                           'cause': err_msg})
    pass


class PfScopeEnd(ParserFunction):
    def parse(self, parser, state):
        err_msg = lang.text('Parser.Error.Scope.UnexpectedEndMarker') %\
                            keywords.scope_end
        raise ParserError({'row': state.row, 'col': state.col - 1, 'file':
                           state.filename, 'path': state.filepath,
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
    def parse(self, parser_i, state):
        module_name = parser_i.match_verbatim_scope(state)
        fpath = os.path.dirname(module_name)
        fname = os.path.basename(module_name)
        found = False
        for folder in parser_i.include_path:
            for ext in keywords.ctx_file_extensions:
                npath = os.path.join(folder, fpath)
                nname = fname + '.' + ext
                if os.path.isfile(os.path.join(npath, nname)):
                    fpath, fname = npath, nname
                    found = True
                    break
            if found:
                break
        # no module found
        if not found:
            err_msg = lang.text('Parser.Error.Library.FileNotFound')
            raise ParserError({'row': state.row, 'col': state.col - 1, 'file':
                               state.filename, 'path': state.filepath,
                               'cause': err_msg})
        # parse library and load functions into file
        absp = os.path.join(fpath, fname)
        fhandle = open(absp, 'r', encoding=keywords.ctx_file_encoding)
        fcontent = fhandle.read()
        fhandle.close()
        subp = kernel.Parser(filepath=fpath,
                             filename=fname,
                             document=fcontent,
                             target=parser_i.target,
                             include_path=[fpath] + parser_i.include_path)
        subp.parse(functions=state.macros)
        state.macros = subp.state.macros
        return ''
    pass


class PfDefFunction(ParserFunction):
    @staticmethod
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
                               state.filename, 'path': state.filepath,
                               'cause': err_msg})
        return text.strip()

    @staticmethod
    def pfd_lang_args(parser, state, param, out):
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
                                   'file': state.filename, 'path': state.
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
                    raise ParserError({'row': state.row, 'col': state.col - 1,
                                       'file': state.filename, 'path':
                                       state.filepath, 'cause': err_msg})
                # valid and push in
                out['args'].append({'name': arg, 'verbatim': verbatim})
            pass
        return found

    @staticmethod
    def pfd_function_mode(parser, state, param, out):
        if param in keywords.func_proc:
            if out['mode'] != '':
                err_msg = lang.text('Parser.Error.Function.ConflictMode')
                raise ParserError({'row': state.row, 'col': state.col - 1,
                                   'file': state.filename, 'path': state.
                                   filepath, 'cause': err_msg})
            out['mode'] = param
            return True
        return False

    @staticmethod
    def pfd_auto_break(parser, state, param, out):
        if param in keywords.func_brk:
            if out['autobreak'] != '':
                err_msg = lang.text('Parser.Error.Function.ConflictBreak')
                raise ParserError({'row': state.row, 'col': state.col - 1,
                                   'file': state.filename, 'path': state.
                                   filepath, 'cause': err_msg})
            out['autobreak'] = param
            return True
        return False

    @staticmethod
    def parse_function_def(parser, state, text):
        # get function name
        func_name, *fdm_args = text.split(keywords.func_def_marker)
        if len(fdm_args) == 0:
            err_msg = lang.text('Parser.Error.Function.MissingDefMarker')
            raise ParserError({'row': state.row, 'col': state.col, 'file':
                               state.filename, 'path': state.filepath,
                               'cause': err_msg})
        if len(fdm_args) > 1:
            err_msg = lang.text('Parser.Error.Function.TooManyDefMarkers')
            raise ParserError({'row': state.row, 'col': state.col +
                               len(func_name) + len(fdm_args[0]) - 1 +
                               len(keywords.func_def_marker), 'file':
                               state.filename, 'path': state.filepath,
                               'cause': err_msg})
        func_name = func_name.strip()
        params = list(i.strip() for i in fdm_args[0].split(
                      keywords.func_def_split))
        # parse params
        out = {
            'name': func_name,
            'lang': '',
            'args': [],  # {'name': '...', 'verbatim': True}
            'mode': '',
            'autobreak': '',
        }
        for param in params:
            if PfDefFunction.pfd_lang_args(parser, state, param, out):
                continue
            if PfDefFunction.pfd_function_mode(parser, state, param, out):
                continue
            if PfDefFunction.pfd_auto_break(parser, state, param, out):
                continue
            # unknown parameter
            err_msg = lang.text('Parser.Error.Function.UnknownParam')
            raise ParserError({'row': state.row, 'col': state.col - 1,
                               'file': state.filename, 'path': state.
                               filepath, 'cause': err_msg})
        # default values
        if out['lang'] == '':
            out['lang'] = keywords.func_lang_raw
        if out['mode'] == '':
            out['mode'] = keywords.func_proc_src_after
        if out['autobreak'] == '':
            out['autobreak'] = keywords.func_brk_wrapinblk
        return out

    @staticmethod
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
                               state.filename, 'path': state.filepath,
                               'cause': err_msg})
        if state.document[state.pos] != '\n':
            err_msg = lang.text('Parser.Error.Function.ExpectedLineBreak')
            raise ParserError({'row': state.row, 'col': state.col + 1, 'file':
                               state.filename, 'path': state.filepath,
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
                               state.filename, 'path': state.filepath,
                               'cause': err_msg})
        code = '\n'.join(i[min_indent:] for i in lines)
        return params, code

    @staticmethod
    def available_modes(parser):
        modes = {keywords.func_proc_src_after,
                 {'doc': keywords.func_proc_doc_after,
                  'web': keywords.func_proc_web_after
                  }.get(parser.target, '')}
        return modes

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
                               state.filename, 'path': state.filepath,
                               'cause': err_msg})
        func.update_function(parser, state, params, code)
        if is_new and params['mode'] in PfDefFunction.available_modes(parser):
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
                               state.filename, 'path': state.filepath,
                               'cause': err_msg})
        if not params['args'][-1]['verbatim']:
            err_msg = lang.text('Parser.Error.Environment.LastMustVerbatim')
            raise ParserError({'row': state.row, 'col': state.col - 1, 'file':
                               state.filename, 'path': state.filepath,
                               'cause': err_msg})
        # update parameters and code
        if not func.update_config(params):
            err_msg = lang.text('Parser.Error.Function.ParamMismatch')
            raise ParserError({'row': state.row, 'col': state.col - 1, 'file':
                               state.filename, 'path': state.filepath,
                               'cause': err_msg})
        func.update_function(parser, state, params, code)
        if is_new and params['mode'] in PfDefFunction.available_modes(parser):
            state.add_function(fname, func)
        return ''
    pass


class PfEnvironmentBegin(ParserFunction):
    def parse(self, parser, state):
        err_msg = lang.text('Parser.Error.Environment.UnknownEnvironment')
        raise ParserError({'row': state.row, 'col': state.col, 'file':
                           state.filename, 'path': state.filepath,
                           'cause': err_msg})
    pass


class PfEnvironmentEnd(ParserFunction):
    def parse(self, parser, state):
        err_msg = lang.text('Parser.Error.Scope.UnexpectedEndMarker') %\
                            keywords.kw_environment_end
        raise ParserError({'row': state.row, 'col': state.col - 1, 'file':
                           state.filename, 'path': state.filepath,
                           'cause': err_msg})
    pass


class PfParagraph(ParserFunction):
    def parse(self, parser, state):
        output = parser.open_auto_break(state, reopen=True)
        prev_abs = state.autobreak.enabled
        state.autobreak.enabled = False
        tmp = parser.match_parsable_scope(state)
        state.autobreak.mode = prev_abs
        output += tmp + parser.close_auto_break(state)
        return output
    pass


class PfDynamicFunction(ParserFunction):
    def __init__(self):
        self.function_name = None
        self.args_vb = None  # verbatim parse or not
        self.mode = None
        self.py_func = None
        self.raw_func = None
        self.autobreak = None
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
            if self.autobreak != params['autobreak']:
                return False
            return True
        self.function_name = params['name']
        self.args_vb = list(i['verbatim'] for i in params['args'])
        self.mode = params['mode']
        self.autobreak = params['autobreak']
        return True

    def update_function(self, parser, state, params, code):
        fname = params['name']
        args = list(i['name'] for i in params['args'])
        if params['lang'] == keywords.func_lang_py:
            if self.py_func is not None:
                err_msg = lang.text('Parser.Error.Function.ConflictCode')
                raise ParserError({'row': state.row, 'col': state.col - 1,
                                   'file': state.filename, 'path': state.
                                   filepath, 'cause': err_msg})
            self.py_func = jitfunction.JitFunctionPy(fname, args, code)
        elif params['lang'] == keywords.func_lang_raw:
            if self.raw_func is not None:
                err_msg = lang.text('Parser.Error.Function.ConflictCode')
                raise ParserError({'row': state.row, 'col': state.col - 1,
                                   'file': state.filename, 'path': state.
                                   filepath, 'cause': err_msg})
            self.raw_func = jitfunction.JitFunctionRaw(fname, args, code)
        return

    def check_do_exec(self, state):
        return (state.target, self.mode) in {
                ('ctx', keywords.func_proc_src_after),
                ('doc', keywords.func_proc_doc_after),
                ('web', keywords.func_proc_web_after)}

    def process_break(self, parser, state):
        # process autobreak
        res = parser.flush_auto_break(state)
        if state.autobreak.enabled:
            if self.autobreak == keywords.func_brk_wrapinblk:
                res += parser.open_auto_break(state)
            elif self.autobreak == keywords.func_brk_leaveblk:
                res += parser.close_auto_break(state)
        return res

    def call_function(self, parser, state, do_exec, args, res):
        tmp = ''
        if do_exec:
            if self.raw_func is not None:
                tmp = str(self.raw_func.eval(*args))
            elif self.py_func is not None:
                tmp = str(self.py_func.eval(*args))
            if state.target == 'ctx':
                tmp = parser.parse_blob(state, tmp)
            res += tmp
        return res

    def parse(self, parser, state):
        do_exec = self.check_do_exec(state)
        res = self.process_break(parser, state)
        # load arguments
        prev_abs = state.autobreak.enabled
        state.autobreak.enabled = False
        args = []
        for verbatim in self.args_vb:
            if verbatim:
                args.append(parser.match_verbatim_scope(state))
            else:
                args.append(parser.match_parsable_scope(state))
        state.autobreak.enabled = prev_abs
        # call function
        res = self.call_function(parser, state, do_exec, args, res)
        # execute this if not executing
        if not do_exec:
            res += keywords.kw_dyn_function % self.function_name + ''.join(
                   (keywords.scope_begin + i + keywords.scope_end)
                   for i in args)
        return res
    pass


class PfDynamicEnvironment(ParserFunction):
    def __init__(self):
        self.function_name = None
        self.args_vb = []  # verbatim parse or not
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
        do_exec = PfDynamicFunction.check_do_exec(self, state)
        res = PfDynamicFunction.process_break(self, parser, state)
        # load arguments
        prev_abs = state.autobreak.enabled
        state.autobreak.enabled = False
        args = []
        indent = parser.get_current_indent(state)
        for verbatim in self.args_vb[:-1]:
            if verbatim:
                args.append(parser.match_verbatim_scope(state))
            else:
                args.append(parser.match_parsable_scope(state))
        if state.document[state.pos] != '\n':
            err_msg = lang.text('Parser.Error.Environment.ExpectedLineBreak')
            raise ParserError({'row': state.row, 'col': state.col - 1,
                               'file': state.filename, 'path': state.
                               filepath, 'cause': err_msg})
        state.shift_forward('\n')
        fn_end = keywords.kw_dyn_environment_end % self.function_name
        args.append(parser.match_to_next_occurence(state, '\n' + ' ' * indent +
                    fn_end, sub_display_error=fn_end))
        state.autobreak.enabled = prev_abs
        # process indentation on last one
        has_indent = args[-1]
        args[-1] = '\n'.join(i[indent:] for i in has_indent.split('\n'))
        # call function
        res = PfDynamicFunction.call_function(self, parser, state,
                                              do_exec, args, res)
        # execute this if not executing
        if not do_exec:
            res += keywords.kw_dyn_environment_begin % self.function_name
            res += ''.join((keywords.scope_begin + i + keywords.scope_end) for
                           i in args[:-1])
            res += '\n' + args[-1] + '\n' + fn_end
        return res
    pass
