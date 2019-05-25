#!/usr/bin/env python3

# quick and ditry script to just show hits
# based on work by Stephan Kuschel, Matt Ware, Catherine Saladrigas, Christian Peltz 2019

import numpy as np
import pyqtgraph as pg
import sqs_nqs_tools.online as online
import sqs_nqs_tools as tools
from pyqtgraph.ptime import time

from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread, QThreadPool)
from pyqtgraph.Qt import QtGui, QtCore
#import PyQt5.QtGui

#from pyqtgraph.Qt import QtGui, QtCore, QtRunnable

#@xfel.filter
#def filterbywhatever(ds, thres=5):
#    '''
#    Place holder for outlier rejection
#    '''
#    if whatever(d) < thres:
#        return True

@online.pipeline
def foldTofs(d):
    '''
    fold all the tofs from a train into a singal tof
    '''
    tof = d['tof']
    
    tofLength = 66000
    startSamples = [13264, 79490, 145716, 211942] #the sample where each tof begins
    tofLength = tofLength if np.max(startSamples) + tofLength < len(tof) else len(tof) - np.max(startSamples)

    newTof = np.zeros(tofLength)

    for s in startSamples:
        print('startSample = {}, lowest peak = {}'.format(s, np.argmin(tof[s:s+tofLength])+s))
        newTof += np.squeeze(tof[s:s+tofLength])
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
    tofBuffer(d['tof']) #add the tof to the hit buffer
    bestTof(d['tof'], -np.min(d['tof'])) #add tat the best hit
    lowestTof(-np.min(d['tof'])) #a histogram of tof height
    avgTof(d['tof']) #the average tof
    
    tofFig.plotTofBuffer(tofBuffer) #plot up the hits
 #  bestTofFig.plotTofBuffer(bestTof) #plot up the high scores
    avgPlot.plotTofBuffer(avgTof)
    
    tofInt(np.sum(d['tof'])) #make that integral plot
    tofPlotInt.plot(tofInt)
    
    pg.QtGui.QApplication.processEvents() #make sure it displays
    return d

#1. setup some plots and buffers
imBufferLength = 1
tofBuffer = tools.DataBuffer(imBufferLength) #a buffer to store hits in 

#buffers for highscores
bestTof = tools.SortedBuffer(imBufferLength) #a buffer to store the brightest 

avgTof = tools.Accumulator()
avgPlot = online.TofBufferPlotter(1, 'average ToF')

#the plots
tofFig = online.TofBufferPlotter(imBufferLength, title='4 newest')
#bestTofFig = online.TofBufferPlotter(imBufferLength, title='4 brightest')

#a histogram for tof heights
lowestTof = online.HistogramPlotter(0, 500, 50, title='tof height')

#integral of tof data
tofInt = online.DataBuffer(100)
tofPlotInt = pg.plot(title='ToF Integrals')
    

        
def main(source):
    '''
    Iterate over the datastream served by source
    Input:
        source: ip address as string
    Output:
        none, updates plots
    '''
#    source = 'tcp://10.254.7.40:8001'     


    #ds is the datastream - everything is done in pipeline form

    ds = online.servedata(source) #get the datastream
    ds = online.getTof(ds) #get the tofs 
    ds = foldTofs(ds) #fold tofs from shots in the pulsetrain
#   ds = online.getSomeDetector(ds, name='phoFlux', spec0='SA3_XTD10_XGM/XGM/DOOCS', spec1='pulseEnergy.photonFlux.value') #get a random piece of data
    
    for data in ds: #this could be made into a pipeline maybe
        plotHits(data)    

if __name__=='__main__':
    #parse args and fire main
    main(online.parseSource())






