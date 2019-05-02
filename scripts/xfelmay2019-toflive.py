#!/usr/bin/env python3

# Stephan Kuschel, Matt Ware, Catherine Saladrigas, 2019

import numpy as np
import pyqtgraph as pg
import xfelmay2019 as xfel


@xfel.filter
def filterbywhatever(ds, thres=5):
    '''
    Place holder for outlier rejection
    '''
    if whatever(d) < thres:
        return True



#_tofplot = pg.plot(title='ToF')
def plottof(d):
    '''
    Plots current time of flight data from one shot.
    Updates _tofplot window
    Input:
        tof data
    Output:
        None, updates plot window
    '''
    #print(d.shape)
    _tofplot.plot(d.flatten(), clear=True)
    pg.QtGui.QApplication.processEvents()


_tofplotavg = pg.plot(title='ToF avg {}'.format(xfel.__version__))
tofavg = xfel.RollingAverage(40)
highqavg = xfel.RollingAverage(600)
lowqavg = xfel.RollingAverage(600)
_tofplotint = pg.plot(title='ToF Integrals (mean) {}'.format(xfel.__version__))
def plottofavg(d):
    '''
    Plots rolling average of TOF
    Input:
        tof data
    Output:
        None, updates plot window
    '''
    d = d.flatten()
    tofavg(d)
    if tofavg.n % 1 == 0:
        _tofplotavg.plot(d, pen='r', clear=True, name='last')
        _tofplotavg.plot(np.asarray(tofavg), pen='w', name='avg')
        _tofplotavg.addLegend()
        pg.QtGui.QApplication.processEvents()


def plotintegral(d):
    # Ausgeschnitten ist [262000:290000]
    highq, lowq = np.mean(d[6000:9000]), np.mean(d[16000:18000])
    highqavg(highq)
    lowqavg(lowq)
    _tofplotint.plot(np.asarray(highqavg.data), clear=True, name='highq', pen='r')
    _tofplotint.plot(np.asarray(lowqavg.data), name='lowq', pen='g')
    _tofplotint.addLegend()
    pg.QtGui.QApplication.processEvents()



def main(source, tofbg=None):
    '''
    Iterate over the datastream served by source
    Input:
        source: ip address as string
    Output:
        none, updates plots
    '''
    if tofbg is not None:
        print('tofbg "{}" loaded...'.format(tofbg))
        tofbg = np.load(tofbg)['arr_0'][262000:290000]
        print('tofbg average is {}'.format(np.mean(tofbg)))

    for tof in xfel.getTof(xfel.servedata(source)):
        if tofbg is not None:
            tof = tof - tofbg
        plottofavg(tof)
        plotintegral(tof)


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
    parser.add_argument('--tofbg', type=str, default=None)

    # Parse arguments from command line
    args = parser.parse_args()



    # find the source
    source = args.source
    if source in ipdict:
        source = ipdict[source]
    # Start main function
    main(source, tofbg=args.tofbg)








