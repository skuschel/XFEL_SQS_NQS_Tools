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
        def ret(gen):
            from multiprocessing import Pool
            pool = Pool(workers)
            readidx = 0
            writeidx = 0
            clen = workers + 1
            cache = [None] * clen
            for el in gen:
                cache[writeidx] = pool.apply_async(f, (el,))
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
                    pool.shutdown()
                    return
        return ret
    return decorator

