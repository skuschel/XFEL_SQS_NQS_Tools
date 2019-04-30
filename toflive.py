#!/usr/bin/env python3

# Stephan Kuschel, Matt Ware, Catherine Saladrigas, 2019

import numpy as np
import pyqtgraph as pg
import helper
import generatorpipeline as gp


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


#@gp.pipeline_parallel()  #does not work due to pickling error of the undecorated function
def _getTof(streamdata):
    data, meta = streamdata
    ret = data['SQS_DIGITIZER_UTC1/ADC/1:network']['digitizers.channel_1_A.raw.samples']
    return ret[262000:290000]
getTof = gp.pipeline_parallel(1)(_getTof)  # this works



_tofplot = pg.plot(title='ToF')
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
    _tofplot.plot(d, clear=True)
    pg.QtGui.QApplication.processEvents()


_tofplotavg = pg.plot(title='ToF avg')
tofavg = helper.RollingAverage(500)
def plottofavg(d):
    '''
    Plots rolling average of TOF
    Input:
        tof data
    Output:
        None, updates plot window
    '''
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

    for tof in getTof(servedata(source)):
		# Update TOF from current shot
        plottof(tof)

		# Update TOF running average using current shot
        plottofavg(tof)




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








