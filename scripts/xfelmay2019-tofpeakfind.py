#!/usr/bin/env python3

# Matthew Ware 2019

# Import required libraries
import numpy as np
import pyqtgraph as pg
import xfelmay2019 as xfel






def main(source):
    '''
    Iterate over the datastream served by source
    Input:
        source: ip address as string
    Output:
        none, updates plots
    '''

    for tof in xfel.baselinedTOF(xfel.servedata(source)):
        pass


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()

    # Default IP is for locally hosted data
    default='tcp://127.0.0.1:9898'

    ipdict = {'live': 'tcp://10.253.0.142:6666'}

    # Define how to parse command line input
    parser.add_argument('source', 
						type=str, 
						help='the source of the data stream. Default is "{}"'.format(default),
           				default=default, 
						nargs='?')

    # Parse arguments from command line
    args = parser.parse_args()

    # find the source
    source = args.source
    if source in ipdict:
        source = ipdict[source]
    # Start main function
    main(source)



