#!/usr/bin/env python3

# Script for Live Analysis of TOF data looking for hits
# based on work by Stephan Kuschel, Matt Ware, Catherine Saladrigas, Christian Peltz 2019
import time as t

import numpy as np
import pyqtgraph as pg
import sqs_nqs_tools.online as online
import sqs_nqs_tools as tools
from sqs_nqs_tools.experimentDefaults import defaultConf
from pyqtgraph.ptime import time

from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread, QThreadPool)
from pyqtgraph.Qt import QtGui, QtCore


## PARAMETERS
tof_hit_threshold = 250  # when the max(abs(tof_trace)) overcomes this threshold it is counted as a hit
tof_range = defaultConf['tofRange'] # alternatively specified as [first sample, last sample]
 
@online.pipeline
def foldTofs(d):
    '''
    fold all the tofs from a train into a singal tof
    
    takes each single tof spectrum from train and sums them all together
    to return a single "single-bunch-like" tof trace into the data stream
    
    Please set the parameters according your current experimental situation
    '''
    # Parameters
    tofLength = 66000 # Length of a single ToF Trace
    startSamples = [13264, 79490, 145716, 211942] # the sample where each tof begins 
    
    tof = d['tof'] # retrieve the tof data
    tofLength = tofLength if np.max(startSamples) + tofLength < len(tof) else len(tof) - np.max(startSamples)

    newTof = np.zeros(tofLength) # empty tof trace ready for the folded data
    # sum them all together into the new trace
    for s in startSamples:
        print('startSample = {}, lowest peak = {}'.format(s, np.argmin(tof[s:s+tofLength])+s))
        newTof += np.squeeze(tof[s:s+tofLength])
    # add the new trace back into datastream replacing the initial trace
    d['tof'] = newTof
    return d

def plotHits(d):
    '''
    Plots current time of flight data from one shot.
    Updates _tofplot window
    Input:
        image data
    Output:
        None, updates plot window
    '''
    ## Load the buffers
    lowestTof(-np.min(d['tof']))  # a histogram of tof height (add Data and Plot)    
    tofBuffer(np.max(np.asarray(-d['tof']))> tof_hit_threshold)  # add 1 if shot is a hit and 0 if not (each trace in tofBuffer overcomming the to_hit_threshold gets a 1 others 0)
    hitBuf(np.sum(np.asarray(tofBuffer)) / tofBuffer.length * 100) # add sum over boolean tof buffer to hitrate buffer and convert to hitrate in percent    
    tofInt(-np.sum(d['tof']))  # add TOF trace Integral value to buffer
    tofHeight(-np.min(d['tof']))  # add TOF trace height ot buffer
    
    ## PLOT the data
    # plot the most recent hit in bestTofFig
    if (-np.min(d['tof']) > tof_hit_threshold):
        bestTof(d['tof'])
        bestTofFig.plotTofBuffer(bestTof) 
    
    tofIntPlot.setData(np.asarray(tofInt))  # plot tof trace integral buffer
    tofHeightPlot.setData(np.asarray(tofHeight))  # plot tof trace height buffer
    hitBufPlot.setData(np.asarray(hitBuf))  # plot tof hitrate buffer
    
    ## Process Events
    pg.QtGui.QApplication.processEvents() # make sure it displays
    return d

# Setup plots and Buffers
## Hit rate
tofBuffer = tools.DataBuffer(100) # a buffer to store tof traces for hitrate determination
hitBuf = online.DataBuffer(10000) # a buffer to store the actual hitrates
hitWin = win = pg.GraphicsWindow() # a window for the hitrates
hitBufPlot = hitWin.addPlot(title='Hitrate in % - hit threshold (height): {}'.format(tof_hit_threshold)).plot() # a plot for the hitrates

## Trace of the last found Hit
bestTof = tools.DataBuffer(1) #a buffer to store the brightest 
bestTofFig = online.TofBufferPlotter(1, title='Last hit ToF  - hit threshold (height): {}'.format(tof_hit_threshold))

## a histogram for tof heights
lowestTof = online.HistogramPlotter(0, 4000, 100, title='ToF heights - Histogram') # from 0 to 4000 with 100 bins

## most recent full integrals of tof data 
tofInt = online.DataBuffer(1000)
intWin = win = pg.GraphicsWindow()
tofIntPlot = intWin.addPlot(title='Recent ToF Integrals').plot()

## most recent (max/min) Heights of tof data 
tofHeight = online.DataBuffer(1000)
heightWin = win = pg.GraphicsWindow()
tofHeightPlot = heightWin.addPlot(title='Recent ToF Heights').plot()
        
def main(source):
    '''
    Iterate over the datastream served by source
    Input:
        source: ip address as string
    Output:
        none, updates plots
    '''
    #ds is the datastream - everything is done in pipeline form

    ds = online.servedata(source) #get the datastream
    ds = online.getTof(ds, idx_range=tof_range) #get the tofs 
    
    #~ Option to let multi bunch tof trace appear like a single bunch tof trace but actually containing a sum of each bunches trace
    #~ ds = foldTofs(ds) #fold tofs from shots in the pulsetrain
    
    #~ Example on how to add some other detector to the datastream
    #~ ds = online.getSomeDetector(ds, name='phoFlux', spec0='SA3_XTD10_XGM/XGM/DOOCS', spec1='pulseEnergy.photonFlux.value')
    
    #~ Run the live analysis
    for data in ds:
        plotHits(data)    

if __name__=='__main__':
    #parse args and fire main
    main(online.parseSource())







