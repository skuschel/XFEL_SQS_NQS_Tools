#!/usr/bin/env python3

import numpy as np

import sqs_nqs_tools.online as online
import sqs_nqs_tools as tools

import pyqtgraph as pg

## select data source (live or emulated live stream)
source = 'tcp://10.253.0.142:6666' # live
#source = 'tcp://127.0.0.1:8002' # emulated

def plotTOF(d):
    _tofplot.plot(d.flatten(), clear=True)
    pg.QtGui.QApplication.processEvents()

def integral(d, int_range=[400000,450000]):
    int_val = np.sum(d[int_range[0]:int_range[1]])
    


## initialize plot windows
### tofplot
_tofplot = pg.plot(title='ToF Simple Live {}'.format(tools.__version__))

## initialize some global lists
_int_value_list = list()
_scan_paramter_list = list()

## setup the pipeline
ds = online.servedata(source) #get the datastream
ds = online.getTof(ds, idx_range=[0,1200000]) #get the tofs
ds = online.getSomeDetector(ds, name='parker', spec0='SQS_NQS_CRSC/TSYS/PARKER_TRIGGER', spec1='actualDelay.value') #get a random piece of data

## start pulling the data
for data in ds: #this could be made into a pipeline maybe
        tof = data['tof']
        parker = data['parker']
        print(parker)
        plotTOF(tof)
        #_int_value_list.append(integral(tof, int_range=[400000,450000]))
        
