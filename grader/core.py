import os
import inspect
from functools import wraps
from collections import OrderedDict
from .code_runner import runTester
from .utils import beautifyDescription, dump_json

CURRENT_FOLDER = os.path.dirname(__file__)

testcases = OrderedDict()

def reset():
    " resets settings and loaded tests "
    global testcases
    testcases = OrderedDict()

def test(test_function):
    """ Decorator for a test. The function should take a single argument which
        is the object containing stdin, stdout and module (the globals of users program).

        The function name is used as the test name, which is a description for the test 
        that is shown to the user. If the function has a docstring, that is used instead.

        Raising an exception causes the test to fail, the resulting stack trace is
        passed to the user. """
    assert hasattr(test_function, '__call__'), \
        "test_function should be a function, got "+repr(test_function)

    @wraps(test_function)
    def wrapper(module, *args, **kwargs):
        if module.caughtException:
            raise module.caughtException
        result = test_function(module, *args, **kwargs)
        if module.caughtException:
            raise module.caughtException
        return result

    testcases[get_test_name(test_function)] = wrapper
    return wrapper


def get_test_name(function):
    """ Returns the test name as it is used by the grader. """
    name = function.__name__
    if inspect.getdoc(function):
        name = beautifyDescription(inspect.getdoc(function))
    return name

### Hooks 

def before_test(action):
    """ Decorator for a hook on a tested function. Makes the tester execute
        the function `action` before running the decorated test. """
    def _inner_decorator(test_function):
        #print("before_test decorating", test_function)
        test_function.__before_hooks__ = get_before_hooks(test_function) + [action]
        return test_function
    return _inner_decorator

def after_test(action):
    """ Decorator for a hook on a tested function. Makes the tester execute
        the function `action` after running the decorated test. """
    def _inner_decorator(test_function):
        #print("after_test decorating", test_function)
        test_function.__after_hooks__ = get_after_hooks(test_function) + [action]
        return test_function
    return _inner_decorator

def get_before_hooks(test_function):
    """ Returns a tuple of functions to run before running `test_function`. """
    return getattr(test_function, '__before_hooks__', [])

def get_after_hooks(test_function):
    """ Returns a tuple of functions to run before running `test_function`. """
    return getattr(test_function, '__after_hooks__', [])

### Exposed methods to test files/code

def test_module(tester_module, user_module, working_dir = None, print_result = False):
    results = runTester(tester_module, user_module, working_dir)
    if print_result:
        print(dump_json(results))
    return results


def test_code(tester_module, user_code, working_dir = None, print_result = False):
    from .utils import tempModule
    with tempModule(user_code, working_dir) as user_module:
        return test_module(tester_module, user_module, working_dir, print_result)