#!/usr/bin/env python3

# Matthew Ware 2019

# Import required libraries
import numpy as np
import pyqtgraph as pg
import xfelmay2019 as xfel


navg = 10
nbins=1000
tofavg = xfel.RollingAverage(navg)
tofhist = xfel.RollingAverage(10)
_tofplotpeak = pg.plot(title='ToF Peak Histogram')
centers = None
def plottofhist(tof):
    tof = tof.flatten()
    tofavg(tof)
    currAvg = np.asarray(tofavg)
    _tofplotpeak.plot(np.abs(currAvg) /np.abs(currAvg).max(), pen='r', clear=True, name='Avg')

    if tofavg.n % navg == 0:
        zf, zguess = xfel.findTOFPeaks( currAvg )
        hist, edges = np.histogram( zf, bins=nbins, range=(0, currAvg.size), weights=zguess )       
        centers = edges[1:] - (edges[1]-edges[0])/2. 

        tofhist(hist)
        
    
    if tofavg.n >= navg:
        centers = np.linspace( 0, currAvg.size, nbins )
        _tofplotpeak.plot(centers, np.asarray(tofhist)/np.asarray(tofhist).max(), pen='w', name='Peak positions histogram')
    
    pg.QtGui.QApplication.processEvents()


def main(source):
    '''
    Iterate over the datastream served by source
    Input:
        source: ip address as string
    Output:
        none, updates plots
    '''
    ds = xfel.servedata(source)
    ds = xfel.baselinedTOF(ds)
    for idx,tof in enumerate(ds):
        plottofhist(tof)



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



