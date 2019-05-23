'''
This module contains function to turn worker functions (working on a single dataset) into functions acepting an iterable and beeing a generator in itself. This way it becomes easy to act on multiple elements and dont have to care how the iteration over the elements works. This makes it possible to parallize worker functions over the elements (=shots) automatically by just changing the decorator.

Todo: A filter decorator to drop shots.

Stephan Kuschel, 2019
'''


import functools


def pipeline(f):
    '''
    A dectorator to change an element wise worker function into a pipeline, which
    expects a generator and is a generator in itself.
    '''
    @functools.wraps(f)
    def ret(gen, **kwds):
        for el in gen:
            yield f(el, **kwds)
    return ret

def filter(f):
    '''
    A function return True or False will be turned into a filter by this generator.
    '''
    @functools.wraps(f)
    def ret(gen):
        for el in gen:
            if bool(f(el)):
                yield el
    return ret


def pipeline_parallel(workers=4):
    '''
    Decorator Factory. The returned decorator distributes the work among `workers` many
    workers. Falls back to the `pipeline` decorator if `workers==1`

    The work is distributed and collected in a round-robin fashin. Thus the
    order of elements is preserved.
    '''
    if workers == 1:
        return pipeline
    def decorator(f):
        @functools.wraps(f)
        def ret(gen, **kwargs):
            from multiprocessing import Pool
            pool = Pool(workers)
            readidx = 0
            writeidx = 0
            clen = workers + 1
            cache = [None] * clen
            for el in gen:
                cache[writeidx] = pool.apply_async(f, (el,), kwargs)
                writeidx = (writeidx + 1) % clen
                if writeidx != readidx:
                    # fill cache
                    continue
                yield cache[readidx].get()
                readidx = (readidx + 1) % clen
            # flush cache
            while True:
                yield cache[readidx].get()
                readidx = (readidx + 1) % clen
                if readidx == writeidx:
                    pool.close()
                    return
        return ret
    return decorator

