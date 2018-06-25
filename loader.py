
import os

import keywords
import modules
import parser

from error import ParserError


def make_default_functions():
    state = parser.ParserState()
    state.add_function(keywords.ch_escape, modules.PfChEscape())
    state.add_function(keywords.ch_whitespace, modules.PfChWhitespace())
    state.add_function(keywords.ch_unescape, modules.PfChUnescape())
    state.add_function(keywords.ch_comment, modules.PfChComment())
    state.add_function(keywords.ch_uncomment, modules.PfChUncomment())
    state.add_function(keywords.scope_begin, modules.PfScopeBegin())
    state.add_function(keywords.scope_end, modules.PfScopeEnd())
    state.add_function(keywords.ch_scope_begin_esc,
                       modules.PfChScopeBeginEsc())
    state.add_function(keywords.ch_scope_end_esc, modules.PfChScopeEndEsc())
    state.add_function(keywords.kw_load_library, modules.PfLoadLibrary())
    state.add_function(keywords.kw_def_function, modules.PfDefFunction())
    state.add_function(keywords.kw_def_environment, modules.PfDefEnvironment())
    state.add_function(keywords.kw_environment_begin,
                       modules.PfEnvironmentBegin())
    state.add_function(keywords.kw_environment_end, modules.PfEnvironmentEnd())
    state.add_function(keywords.kw_paragraph, modules.PfParagraph())
    return state.macros


def parse_file(path, target):
    fhandle = open('test.tex', 'r', encoding=keywords.ctx_file_encoding)
    fcontent = fhandle.read()
    fhandle.close()
    pobj = parser.Parser(filepath=os.path.dirname(path),
                         filename=os.path.basename(path),
                         document=fcontent,
                         target=target,
                         include_path=keywords.ctx_include_path)
    output = pobj.parse(functions=make_default_functions())
    return output

s = parse_file('./test.tex', 'web')
print(s)
