#!/usr/bin/env python3

# quick and ditry script to just show hits
# based on work by Stephan Kuschel, Matt Ware, Catherine Saladrigas, Christian Peltz 2019
import time as t

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
    tofBuffer(-d['tof']) #add the tof to the hit buffer
    #add tat the best hit
    lowestTof(-np.min(d['tof'])) #a histogram of tof height
    avgTof(d['tof'].flatten()) #the average tof
#    print(np.sum((np.max(np.asarray(tofBuffer), axis=1)) > 1000))
    hitBuf(np.sum((np.max(np.asarray(tofBuffer), axis=1)) > 1400))
    
    if (-np.min(d['tof']) > 1400):
        bestTof(d['tof'])
        bestTofFig.plotTofBuffer(bestTof)
    
    #n += 1
#    if tofInt.n%1 == 0:
#        tofFig.plotTofBuffer(tofBuffer) #plot up the hits
 #  bestTofFig.plotTofBuffer(bestTof) #plot up the high scores
#        avgPlot.plotTofBuffer(avgTof)
    
    tofInt(-np.min(d['tof'])) #make that integral plot
    tofPlotInt.setData(np.asarray(tofInt))
    hitBufPlot.setData(np.asarray(hitBuf))
    pg.QtGui.QApplication.processEvents() #make sure it displays
    return d

#1. setup some plots and buffers
imBufferLength = 2
tofBuffer = tools.DataBuffer(imBufferLength) #a buffer to store hits in 

#buffers for highscores
bestTof = tools.DataBuffer(1) #a buffer to store the brightest 

avNum = 30
avgTof = tools.RollingAverage(avNum)
#avgPlot = online.TofBufferPlotter(1, '{} ToF rolling average'.format(avNum))

#the plots
tofFig = online.TofBufferPlotter(imBufferLength, title='Latest ToF')
bestTofFig = online.TofBufferPlotter(1, title='hit ToF')

#a histogram for tof heights
lowestTof = online.HistogramPlotter(0, 4000, 100, title='tof height')

#integral of tof data
tofInt = online.DataBuffer(1000)
intWin = win = pg.GraphicsWindow()
tofPlotInt = intWin.addPlot(title='ToF Integrals').plot()

#integral of hit rate
hitBuf = online.DataBuffer(50000)
hitWin = win = pg.GraphicsWindow()
hitBufPlot = hitWin.addPlot(title='Hits in last {} shots'.format(imBufferLength)).plot()

        
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
#    ds = foldTofs(ds) #fold tofs from shots in the pulsetrain
#   ds = online.getSomeDetector(ds, name='phoFlux', spec0='SA3_XTD10_XGM/XGM/DOOCS', spec1='pulseEnergy.photonFlux.value') #get a random piece of data
    t_0 = t.time()
    t.sleep(0.01)
    t_1 = t.time()
    for data in ds: #this could be made into a pipeline maybe
        print([t.time() - t_0, t_1 - t_0])
        t_0 = t.time()
        plotHits(data)    
        t_1 = t.time()

if __name__=='__main__':
    #parse args and fire main
    main(online.parseSource())







