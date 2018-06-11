
# header markers
header_marker_begin = '---'
header_entry_separator = '|'
header_marker_end = '---'

# scope markers
scope_begin = '{'
scope_end = '}'

# special characters
ch_escape = '\\'
ch_whitespace = '\\ '
ch_unescape = '\\\\'
ch_comment = '%'
ch_uncomment = '\\%'
ch_scope_begin_esc = '\\{'
ch_scope_end_esc = '\\}'

# builtin keywords / functions
kw_load_library = '\\usepackage'
kw_namespace = '\\namespace'
kw_def_function = '\\newcommand'
kw_environment_begin = '\\begin'
kw_environment_end = '\\end'

# function related
func_def_marker = ':'
func_lang_py = 'py'
func_lang_js = 'js'  # not yet implemented
func_lang_raw = 'raw'
func_param_left = '('
func_param_right = ')'
func_param_split = ','
func_proc_src_before = 'src->ctx'
func_proc_src_after = 'ctx->ctx'
func_proc_doc_before = 'ctx->doc'
func_proc_doc_after = 'doc->doc'
func_proc_web_before = 'ctx->web'
func_proc_web_after = 'web->web'
func_verbatim = 'verbatim'

# namespace related
ns_marker = '@'
