'''
Pipeline tools when using generators for pipelines in python

Stephan Kuschel, 2019
'''


import functools


def pipeline(f):
    '''
    A dectorator to change an element wise worker function into a pipeline, which
    expects a generator and is a generator in itself.
    '''
    @functools.wraps(f)
    def ret(gen):
        for el in gen:
            yield f(el)
    return ret
