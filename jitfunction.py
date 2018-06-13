
import keywords
import misc


class JitFunctionPy:
    """Function wrapper dynamically loaded through raw Python code and can be
    executed instantly with given parameters."""
    class GlobalVariableStorage:
        def __init__(self):
            def initvar(self, name, val):
                if not hasattr(self, name):
                    setattr(self, name, val)
                return
            setattr(self, keywords.jit_py_globals_initfunc, initvar)
            return
        pass

    def report_argument_cnt_mismatch(function_name, arguments, args):
        # exceeded arguments
        if len(args) > len(arguments):
            err_msg = '%s() takes %d positional arguments but %d were given' %\
                      (function_name, len(arguments), len(args))
            raise TypeError(err_msg)
        # insufficient arguments
        elif len(args) < len(arguments):
            delta = len(arguments) - len(args)
            if delta == 1:
                err_msg = ": '%s'" % arguments[-1]
            elif delta == 2:
                err_msg = "s: '%s' and '%s'" % (arguments[-2], arguments[-1])
            else:
                err_msg = "s: %sand '%s'" % (''.join(("'%s', " % i) for i in
                                             arguments[-delta:-1]),
                                             arguments[-1:][0])
            err_msg = '%s() missing %d required positional argument' %\
                      (function_name, delta) + err_msg
            raise TypeError(err_msg)
        return

    def __init__(self, function_name, arguments, code):
        """Initialize dynamic function and compile code.
        @param function_name(str) function name
        @param arguments(list(str)) arguments to be used by this function,
            must correspond to the ones used in the function
        @param code(str) python code
        @throws SyntaxError"""
        self.function_name = function_name
        self.arguments = arguments
        self.code = code
        # set global variables, default to None
        self.globals = JitFunctionPy.GlobalVariableStorage()
        # create execution script
        script = 'def __function__(%s):\n' % ', '.join(arguments)\
                 + '%s\n' % '\n'.join((' ' * 4 + i) for i in code.split('\n'))\
                 + '__result__ = __function__(*__args__)'
        # compile script
        self.binary = compile(script, '<string>', 'exec')
        return

    def eval(self, *args):
        """Execute function and returns result.
        @param *args positional arguments to call the dynamic function
        @returns ... depending on function behavior
        @throws TypeError when positional arguments' number doesn't match
        @throws ... depending on function behavior"""
        JitFunctionPy.report_argument_cnt_mismatch(self.function_name,
                                                   self.arguments, args)
        # execute function
        locals = {'__args__': args}
        globs = {keywords.jit_py_globals_classname: self.globals}
        exec(self.binary, globs, locals)
        return locals['__result__']
    pass


class JitFunctionRaw:
    """Function wrapper that substitutes arguments starting with # chars."""

    def __init__(self, function_name, arguments, code):
        """Initialize dynamic function and compile code.
        @param function_name(str) function name
        @param arguments(list(str)) arguments to be used by this function,
            must correspond to the ones used in the function
        @param code(str) subsitute string"""
        self.function_name = function_name
        self.arguments = arguments
        self.code = code
        # stack tuples: (is_string_or_not, ...)
        #   string:     (bool(True), str(code))
        #   not string: (bool(False), int(argument_id))
        stack = [(True, self.code)]
        # split code with stack
        for i in range(0, len(self.arguments)):
            var = keywords.jit_raw_variable % self.arguments[i]
            new_stack = []
            for is_string, data in stack:
                if not is_string:
                    new_stack.append((is_string, data))
                    continue
                strs = list((True, i) for i in data.split(var))
                strs = misc.listjoin((False, i), strs)
                for s in strs:
                    if s != (True, ''):
                        new_stack.append(s)
            stack = new_stack
        # update binary with this (somehow unreadable) format
        self.binary = stack
        return

    def eval(self, *args):
        """Execute function and returns result.
        @param *args positional arguments to call the dynamic function
        @returns output(str)
        @throws TypeError when positional arguments' number doesn't match"""
        JitFunctionPy.report_argument_cnt_mismatch(self.function_name,
                                                   self.arguments, args)
        # substitute arguments
        result = ''
        for is_string, data in self.binary:
            if is_string:
                result += data
            else:
                result += str(args[data])
        return result
    pass
