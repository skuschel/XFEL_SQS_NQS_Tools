#!/usr/bin/env python3
# Monitors if the TOF and MCP datastreams are alive
# Stephan Kuschel, Matt Ware, Catherine Saladrigas, 2019

import numpy as np
import pyqtgraph as pg
import sqs_nqs_tools.online as xfel
import time

_daqaliveplot = pg.image(title='DAQ alive: Green good, red bad')
CLRS = ['r','g']
cmap = pg.ColorMap(np.array([0.,1.]), np.array([pg.colorTuple(pg.Color(c)) for c in CLRS ]) )
_daqaliveplot.setColorMap( cmap )
def plotdaqalive(status):
    '''
    Plots red/green image depending on value of status
    Input:
	ds
    Output:
        None, updates plot window
    '''
    im = np.ones((3,3))*float(status)
    _daqaliveplot.setImage( im, autoLevels=False )
    pg.QtGui.QApplication.processEvents()

def isAlive(ds):
    # Attempt to get the detector
    try:
        xfel.getSomeDetector(ds, spec0='SQS_DPU_LIC/CAM/YAG_UPSTR:daqOutput', spec1='data.image.pixels')
        #xfel.getSomeDetector(ds, spec0='SQS_DPU_LIC/CAM/YAG_UPSTR:output', spec1='data.image.data')
    except Exception as exc:
        print(str(exc))
        print('MCP DATA SOURCE CHANGED!!!')
        print('MCP DATA SOURCE CHANGED!!!')
        print('MCP DATA SOURCE CHANGED!!!')
        return False

    # Attempt to get the TOF
    try:
        xfel.getSomeDetector(ds, spec0='SQS_DIGITIZER_UTC1/ADC/1:network', spec1='digitizers.channel_1_A.raw.samples')
    except Exception as exc:
        print('TOF DATA SOURCE CHANGED!!!')
        print('TOF DATA SOURCE CHANGED!!!')
        print('TOF DATA SOURCE CHANGED!!!')
        return False

    # If both succeed return true
    return True

def main(source):
    '''
    Iterate over the datastream served by source
    Input:
        source: ip address as string
    Output:
        none, updates plots
    '''
    for i, ds in enumerate((xfel.servedata(source))):
        plotdaqalive( isAlive(ds) )

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








