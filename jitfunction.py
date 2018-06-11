
class JitFunction(object):
    """ JitFunction is a function dynamically loaded through raw Python code
    and can be executed instantly with given parameters."""

    def __init__(self, function_name, arguments, global_vars, code):
        """Initialize dynamic function and compile code.
        @param function_name(str) function name
        @param arguments(list(str)) arguments to be used by this function,
            must correspond to the ones used in the function
        @param global_vars(list(str)) enumeration of global variables at
            initialization, set to None before first run
        @param code(str) python code
        @returns None
        @throws ???"""

        self.function_name = function_name
        self.arguments = arguments
        self.code = code
        # set global variables, default to None
        self.globals = {}
        for i in global_vars:
            self.globals[i] = None
        # create execution script
        script = 'def __function__(%s):\n' % ', '.join(arguments)\
                 + '%s\n' % '\n'.join((' ' * 4 + i) for i in code.split('\n'))\
                 + '__result__ = __function__(*__args__)'
        # compile script
        self.binary = compile(script, '<string>', 'exec')  # TODO: exceptions?
        return

    def eval(self, *args):
        """Execute function and returns result.
        @param *args positional arguments to call the dynamic function
        @returns ... depending on function behavior
        @throws TypeError when positional arguments' number doesn't match
        @throws ... depending on function behavior"""

        # exceeded arguments
        if len(args) > len(self.arguments):
            err_msg = '%s() takes %d positional arguments but %d were given' %\
                      (self.function_name, len(self.arguments), len(args))
            raise TypeError(err_msg)
        # insufficient arguments
        elif len(args) < len(self.arguments):
            delta = len(self.arguments) - len(args)
            if delta == 1:
                err_msg = ": '%s'" % self.arguments[-1]
            elif delta == 2:
                err_msg = "s: '%s' and '%s'" % (self.arguments[-2],
                                                self.arguments[-1])
            else:
                err_msg = "s: %sand '%s'" % (''.join(("'%s', " % i) for i in
                                             self.arguments[-delta:-1]),
                                             self.arguments[-1:][0])
            err_msg = '%s() missing %d required positional argument' %\
                      (self.function_name, delta) + err_msg
            raise TypeError(err_msg)
        # execute function
        locals = {'__args__': args}
        exec(self.binary, self.globals, locals)
        return locals['__result__']
    pass
