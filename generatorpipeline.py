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



import functools
def pipeline_parallel(max_workers=4):
    '''
    Decorator Factory. The returned decorator distributes the work among `max_workers` many
    workers. Falls back to the `pipeline` decorator if `max_workers==1`

    The work is distributed and collected in a round-robin fashin. Thus the
    order of elements is preserved.
    '''
    if max_workers == 1:
        return pipeline
    def decorator(f):
        @functools.wraps(f)
        def ret(gen):
            from concurrent.futures import ProcessPoolExecutor
            pool = ProcessPoolExecutor(max_workers=max_workers)
            readidx = 0
            writeidx = 0
            clen = max_workers + 1
            cache = [None] * clen
            for el in gen:
                cache[writeidx] = pool.submit(f, el)
                writeidx = (writeidx + 1) % clen
                if writeidx != readidx:
                    # fill cache
                    continue
                yield cache[readidx].result()
                readidx = (readidx + 1) % clen
            # flush cache
            while True:
                yield cache[readidx].result()
                readidx = (readidx + 1) % clen
                if readidx == writeidx:
                    return
        return ret
    return decorator
