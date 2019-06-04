#!/usr/bin/env python3

# quick and ditry script to just show hits
# based on work by Stephan Kuschel, Matt Ware, Catherine Saladrigas, Christian Peltz 2019
# derrived from file showHits.py - to be found in the Archive folder

import numpy as np
import pyqtgraph as pg
import sqs_nqs_tools.online as online
import sqs_nqs_tools as tools
from sqs_nqs_tools.experimentDefaults import defaultConf
from pyqtgraph.ptime import time

# parameters
tof_range = defaultConf['tofRange'] # alternatively specified as [first sample, last sample]

def plotData(d):
    '''
    Plots current time of flight data from one shot.
    Updates _tofplot window
    Input:
        image data
    Output:
        None, updates plot window
    '''
    ## Fill Data into Buffers
    tofBuffer(d['tof'])  # add the tof to the tof buffer   
    bestTof(d['tof'], -np.min(d['tof']))  # add the tof to the best shot buffer
    tofInt(np.sum(d['tof']))  # add the integral of tof spectrum to integral buffer
    
    ## Plot Data from buffers
    tofFig.plotTofBuffer(tofBuffer) # plot up the most recent tofs   
    bestTofFig.plotTofBuffer(bestTof) # plot up the high scores
    
    ## Add Data and Plot Histogram
    lowestTofFig(-np.min(d['tof'])) #a histogram of tof height
    
    # make sure the updates get displayed
    pg.QtGui.QApplication.processEvents()
    
    tofIntFig.plot(tofInt) # plot up the most recent integral values

    
    return d

# setup some plots and buffers
## Buffers
tofBuffer = tools.DataBuffer(4)  # a buffer to store most recent shots
bestTof = tools.SortedBuffer(4)  # a buffer to store the brightest shots
tofInt = online.DataBuffer(100)  # a buffer to store the last 100 integral values of spectrum

## Plots
tofFig = online.TofBufferPlotter(tofBuffer.length, title='4 newest')  # a figure to plot the most recent plots
bestTofFig = online.TofBufferPlotter(bestTof.length, title='4 brightest')  # a figure to plot the most brightest plots
lowestTofFig = online.HistogramPlotter(0, 500, 50, title='tof height')  # a histogram for tof heights; from 0 to 500 in 50 bins; (since tof traces point into negative direction this will go for the min value of the whole spectrum)
tofIntFig = pg.plot(title='ToF Integrals')  # a figure / plot for the most recent integral values of spectrum

def main(source):
    '''
    Iterate over the datastream served by source
    Input:
        source: ip address as string
    Output:
        none, updates plots
    '''
       
    ds = online.servedata(source) #get the datastream
    ds = online.getTof(ds, idx_range=tof_range) #get the tofs 
    
    for data in ds:
        plotData(data)
    #ds is the datastream - everything is done in pipeline form

if __name__=='__main__':
    #parse args and fire main
    main(online.parseSource())







