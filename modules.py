
class ParserFunction(object):
    """Function executed at certain substring occurences while parsing.
    @param f_types(set(str)) set of available function modes, including:
        keywords.func_proc_src_before
        keywords.func_proc_src_after
        keywords.func_proc_doc_before
        keywords.func_proc_doc_after
        keywords.func_proc_web_before
        keywords.func_proc_web_after
    @param arguments(list(str)) list of arguments taken"""

    def __init__(self, f_types, arguments):
        self.f_types = f_types
        self.arguments = arguments
        return

    def parse(self, parser, state):
        return
    pass
