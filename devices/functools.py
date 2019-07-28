"""
Replica Python functools, for MicroPython

 * Used for BNO055 library

Found here:
    https://bitbucket.org/thesheep/micropython-bno055/
Original:
    https://github.com/micropython/micropython-lib/blob/master/functools/functools.py
"""


def partial(func, *args, **kwargs):
    def _partial(*more_args, **more_kwargs):
        kw = kwargs.copy()
        kw.update(more_kwargs)
        return func(*(args + more_args), **kw)
    return _partial


def update_wrapper(wrapper, wrapped):
    # Dummy impl
    return wrapper


def wraps(wrapped):
    # Dummy impl
    return lambda x: x

def reduce(function, iterable, initializer=None):
    it = iter(iterable)
    if initializer is None:
        value = next(it)
    else:
        value = initializer
    for element in it:
        value = function(value, element)
    return value