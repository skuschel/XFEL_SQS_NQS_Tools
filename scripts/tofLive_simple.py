#!/usr/bin/env python3

import numpy as np

import sqs_nqs_tools.online as online
import sqs_nqs_tools as tools

import pyqtgraph as pg



source = 'tcp://10.253.0.142:6666' # live
# source = 'tcp://127.0.0.1:8001' # emulated

ds = online.servedata(source) #get the datastream
ds = online.getTof(ds, idx_range=[0,1200000]) #get the tofs / give the index range!

_tofplot = pg.plot(title='ToF Simple Live {}'.format(tools.__version__))

for data in ds: #this could be made into a pipeline maybe
        _tofplot.plot(data['tof'].flatten(), clear=True)
        pg.QtGui.QApplication.processEvents()
