#!/usr/bin/env python3

# Stephan Kuschel, Matt Ware, Catherine Saladrigas, 2019

import numpy as np
import pyqtgraph as pg
import xfelmay2019 as xfel





def main(source, dataf=None, outfile=None, nmax=None):
    '''
    Iterate over the datastream served by source
    Input:
        source: ip address as string
    Output:
        none, updates plots
    '''
    ds = xfel.servedata(source)
    ds = dataf(ds)

    acc = xfel.Accumulator()
    for data, i in zip(ds, range(nmax)):
        if i%10 == 0:
            print('{} / {}'.format(i, nmax))
        acc(data)

    np.savez_compressed('{}-bg{}'.format(outfile, nmax), acc.mean)
    


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()

    # Default IP is for locally hosted data
    default='tcp://127.0.0.1:9898'

    ipdict = {'live': 'tcp://10.253.0.142:6666',
             'local': 'tcp://127.0.0.1:9898'}

    # Define how to parse command line input
    parser.add_argument('source', 
                        type=str, 
                        help='the source of the data stream. Default is "{}"'.format(default),
                        default=default,
                        nargs='?')
    parser.add_argument('data', type=str, choices=['tof'])
    datafdict = {'tof': xfel.getTof}

    parser.add_argument('outfile', type=str)
    parser.add_argument('--nmax', type=int, default=2000)

    # Parse arguments from command line
    args = parser.parse_args()

    # find the source
    source = args.source
    if source in ipdict:
        source = ipdict[source]
    # Start main function
    main(source,
         dataf=datafdict[args.data],
         outfile=args.outfile,
         nmax=args.nmax)








