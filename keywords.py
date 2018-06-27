
# basic specifications
ctx_file_extensions = [
    'ctx',
    'tex',
    'sty',
]
ctx_file_encoding = 'utf-8'
ctx_include_path = [
    '.',
]

# header markers
header_marker_begin = r'^-{3,}$'
header_entry_separator = '|'
header_marker_end = r'^-{3,}$'

# scope markers
scope_begin = '{'
scope_end = '}'

# special characters
ch_escape = '\\'
ch_comment = '%'

# builtin keywords / functions
kw_load_library = '\\usepackage'
kw_def_function = '\\newcommand'
kw_def_environment = '\\newenvironment'
kw_environment_begin = '\\begin'
kw_environment_end = '\\end'
kw_paragraph = '\\paragraph'

kw_dyn_function = ch_escape + '%s'
kw_dyn_environment_begin = kw_environment_begin + scope_begin + '%s' +\
                           scope_end
kw_dyn_environment_end = kw_environment_end + scope_begin + '%s' + scope_end

# function related
func_def_marker = ':'
func_def_split = ';'
func_lang_py = 'py'
func_lang_raw = 'raw'
func_lang = {
    func_lang_py,
    func_lang_raw,
}
func_param_left = '('
func_param_right = ')'
func_param_split = ','
func_param_verbatim = '*'
func_param_forbid_chars = '\n !"#$%&\'()*+,-./:;<=>?[\\]^_`{|}~'
func_proc_src_after = 'ctx->ctx'
func_proc_doc_after = 'ctx->doc'
func_proc_web_after = 'ctx->web'
func_proc = {
    func_proc_src_after,
    func_proc_doc_after,
    func_proc_web_after,
}
func_brk_wrapinblk = 'wrapinblk'  # contained in paragraph
func_brk_leaveblk = 'leaveblk'  # leave paragraph
func_brk = {
    func_brk_wrapinblk,
    func_brk_leaveblk,
}

# jit function related
jit_py_globals_classname = 'glob'
jit_py_globals_initfunc = 'initvar'  # require code change
jit_py_universals_classname = 'univ'
jit_py_universals_initfunc = 'initvar'  # requires code change
jit_raw_variable = '#%s'

# auto break utility
autobrk_para_begin_doc = '\n\\paragraph{}\n'
autobrk_para_end_doc = '\n'
autobrk_para_begin_web = '\n<p>'
autobrk_para_end_web = '</p>\n'

# escape characters
ch_esc_chars = {
    # builtin
    'unescape': {
        'ctx': '\\\\',
        'doc': '\\backslash',
        'web': '\\',
    },
    'space': {
        'ctx': '\\ ',
        'doc': '\\ ',
        'web': '&nbsp;',
    },
    'uncomment': {
        'ctx': '\\%',
        'doc': '\\%',
        'web': '%',
    },
    'scope_begin': {
        'ctx': '\\{',
        'doc': '\\{',
        'web': '{',
    },
    'scope_end': {
        'ctx': '\\}',
        'doc': '\\}',
        'web': '}',
    },
    'dollar': {
        'ctx': '\\$',
        'doc': '\\$',
        'web': '$',
    },
    # web
    'dquote': {
        'ctx': '"',
        'doc': '"',
        'web': '&quot;',
    },
    'ampersand': {
        'ctx': '&',
        'doc': '\\&',
        'web': '&amp;',
    },
    'lt': {
        'ctx': '<',
        'doc': '<',
        'web': '&lt;',
    },
    'rt': {
        'ctx': '>',
        'doc': '>',
        'web': '&rt;',
    },
    # doc
    'lquote': {
        'ctx': '`',
        'doc': '`',
        'web': '‘',
    },
    'rquote': {
        'ctx': '\'',
        'doc': '\'',
        'web': '’',
    },
    'ldquote': {
        'ctx': '``',
        'doc': '``',
        'web': '“',
    },
    'rdquote': {
        'ctx': '\'\'',
        'doc': '\'\'',
        'web': '”',
    },
    'sharp': {
        'ctx': '#',
        'doc': '\\#',
        'web': '#',
    },
    'caret': {
        'ctx': '^',
        'doc': '\\^',
        'web': '^',
    },
    'underline': {
        'ctx': '_',
        'doc': '\\_',
        'web': '_',
    },
    'tilde': {
        'ctx': '~',
        'doc': '\\~',
        'web': '~',
    },
}
