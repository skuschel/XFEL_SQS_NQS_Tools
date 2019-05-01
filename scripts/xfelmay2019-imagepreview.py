#!/usr/bin/env python3

# Stephan Kuschel, Matt Ware, Catherine Saladrigas, 2019

import numpy as np
import pyqtgraph as pg
import xfelmay2019 as xfel


@xfel.filter
def filterbywhatever(ds, thres=5):
    '''
    Place holder for outlier rejection
    '''
    if whatever(d) < thres:
        return True



#_pgimage = pg.image(title='Current Image {}'.format(xfel.__version__))
def plotimage(d):
    '''
    Plots current time of flight data from one shot.
    Updates _tofplot window
    Input:
        image data
    Output:
        None, updates plot window
    '''
    _pgimage.setImage(d, autoRange=False)
    pg.QtGui.QApplication.processEvents()




_pgimage2 = pg.image(title='AverageImage {}'.format(xfel.__version__))
_pghistplot = pg.plot(title='HistBrightness {}'.format(xfel.__version__))
imagehist = xfel.DataBuffer(50)
brightnesshist = xfel.DataBuffer(1000)
def plotbrightest(d):
    '''
    Plots current time of flight data from one shot.
    Updates _tofplot window
    Input:
        image data
    Output:
        None, updates plot window
    '''
    imagehist(d)
    brightnesshist(np.mean(d))
    _pghistplot.plot(brightnesshist.data, clear=True) 
    _pgimage2.setImage(d-imagehist.average, autoRange=False)
    pg.QtGui.QApplication.processEvents()



def main(source):
    '''
    Iterate over the datastream served by source
    Input:
        source: ip address as string
    Output:
        none, updates plots
    '''
    ds = xfel.servedata(source)
    ds = xfel.getImage(ds)
    for image in ds:
        #plotimage(image)
        plotbrightest(image)


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








