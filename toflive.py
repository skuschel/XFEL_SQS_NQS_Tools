#!/usr/bin/env python3

# Stephan Kuschel, Matt Ware, Catherine Saladrigas, 2019

import numpy as np
import pyqtgraph as pg
import helper


def filterbywhatever(ds, thres=5):
    '''
    Place holder for outlier rejection
    '''
    for d in ds:
        if whatever(d) < thres:
            yield d


def servedata(host, type='REQ'):
    '''
    Generator for the online data stream.
    Input: 
        host: ip address of data stream
        type: ???
    Output:
        dictionary of values for current event
    '''
    from karabo_bridge import Client
    # Generate a client to serve the data
    c = Client(host, type)

    # Return the newest event in the datastream using an iterator construct
    for ret in c:
    	yield ret
    

def getTof(data):
    ret = data['SQS_DIGITIZER_UTC1/ADC/1:network']['digitizers.channel_1_A.raw.samples']
    return ret[262000:290000]


_tofplot = pg.plot(title='ToF')
def plottof(data):
    '''
    Plots current time of flight data from one shot.
    Updates _tofplot window
    Input:
        dictionary of data values from stream
    Output:
        None, updates plot window
    '''
    d = getTof(data)
    #print(d.shape)
    _tofplot.plot(d, clear=True)
    pg.QtGui.QApplication.processEvents()


_tofplotavg = pg.plot(title='ToF avg')
tofavg = helper.RollingAverage(50)
def plottofavg(data):
    '''
    Plots rolling average of TOF
    Input:
        dictionary of data values from stream
    Output:
        None, updates plot window
    '''
    d = getTof(data)
    tofavg(d)
    if tofavg.n % 10 == 0:
    	_tofplotavg.plot(np.asarray(tofavg), clear=True)
    	pg.QtGui.QApplication.processEvents()



def main(source):
    '''
    Iterate over the datastream served by source
    Input:
        source: ip address as string
    Output:
        none, updates plots
    '''

    for data, meta in servedata(source):
		# Update TOF from current shot
        plottof(data)

		# Update TOF running average using current shot
        plottofavg(data)




if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()

    # Default IP is for live data
    default='tcp://127.0.0.1:9898'

    # Define how to parse command line input
    parser.add_argument('source', 
						type=str, 
						help='the source of the data stream. Default is "{}"'.format(default),
           				default=default, 
						nargs='?')

    # Parse arguments from command line
    args = parser.parse_args()

    # Start main function using args.soruce
    main(args.source)








