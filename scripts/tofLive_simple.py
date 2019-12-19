#!/usr/bin/env python3

import numpy as np

import sqs_nqs_tools.online as online
import sqs_nqs_tools as tools

import pyqtgraph as pg

# Parameters may to be changed by User
tof_range = [0,200000]

# Main Program
def main(source):
    '''
    Iterate over the datastream served by source
    Input:
        source: ip address as string
    Output:
        none, updates plots
    '''
    ds = online.servedata(source) #get the datastream
    ds = online.getTof(ds, idx_range=tof_range) #get the tofs / give the index range!

    _tofplot = pg.plot(title='ToF Simple Live {}'.format(tools.__version__))

    for data in ds:
            _tofplot.plot(data['tof'].flatten(), clear=True)
            pg.QtGui.QApplication.processEvents()

# Understand input arguments when program started an execute main() which contains the main program
if __name__=='__main__':
    #This translates the input arguments (eg live or offline or custom adress tcp://127.0.0.1:50060) to a source and hands it to the main program
    main(online.parseSource())
