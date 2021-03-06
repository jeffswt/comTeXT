
import os

from . import keywords
from . import modules
from . import kernel

from error import ParserError


def make_default_functions():
    state = kernel.ParserState()
    # add escape characters
    for s in keywords.ch_esc_chars:
        c = keywords.ch_esc_chars[s]
        state.add_function(c['ctx'], modules.PfChEscapedCharacter(c))
    # add builtin functions
    state.add_function(keywords.ch_escape, modules.PfChEscape())
    state.add_function(keywords.ch_comment, modules.PfComment())
    state.add_function(keywords.scope_begin, modules.PfScopeBegin())
    state.add_function(keywords.scope_end, modules.PfScopeEnd())
    state.add_function(keywords.kw_load_library, modules.PfLoadLibrary())
    state.add_function(keywords.kw_def_function, modules.PfDefFunction())
    state.add_function(keywords.kw_def_environment, modules.PfDefEnvironment())
    state.add_function(keywords.kw_environment_begin,
                       modules.PfEnvironmentBegin())
    state.add_function(keywords.kw_environment_end, modules.PfEnvironmentEnd())
    state.add_function(keywords.kw_paragraph, modules.PfParagraph())
    state.add_function(keywords.kw_math_begin, modules.PfMathMode())
    return state.macros


def parse_file(path, target, preload_libs=[], include_path=None):
    if target not in {'ctx', 'doc', 'web'}:
        raise ValueError(target)
    fhandle = open(path, 'r', encoding=keywords.ctx_file_encoding)
    fcontent = fhandle.read()
    fhandle.close()
    if include_path is None:
        include_path = keywords.ctx_include_path
    pobj = kernel.Parser(filepath=os.path.dirname(path),
                         filename=os.path.basename(path),
                         document=fcontent,
                         target=target,
                         include_path=include_path)
    pobj.parse(functions=make_default_functions(),
               preload_libs=preload_libs)
    output = {
        'document': pobj.document,
        'headers': pobj.headers,
    }
    return output
