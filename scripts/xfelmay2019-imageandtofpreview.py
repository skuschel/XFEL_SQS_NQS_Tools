#!/usr/bin/env python3

# Stephan Kuschel, Matt Ware, Catherine Saladrigas, Christian Peltz 2019

import numpy as np
import pyqtgraph as pg
import xfelmay2019 as xfel
from pyqtgraph.ptime import time


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




######_pgimage2 = pg.image(title='AverageImage {}'.format(xfel.__version__))
#win_stat = 
win_live = pg.GraphicsWindow()
_pgbrightestimgtof = win_live.addPlot(row = 0, col = 0)
_pgbrightestimg = win_live.addViewBox(row = 0, col = 1)
_pgstattof = win_live.addPlot(row = 1, col = 0)
_pgstatimg = win_live.addPlot(row = 1, col = 1)



####_pgbrightestimg = pg.image(title='Brightest Shots {}'.format(xfel.__version__))
brightestlen = 15
imagehist = xfel.DataBuffer(brightestlen)
tofhist = xfel.DataBuffer(brightestlen)
tidhist = xfel.DataBuffer(brightestlen)
brightnesshist = xfel.DataBuffer(1000)
tofsignalhist = xfel.DataBuffer(1000)
_brightlasttid = -1
lastTime = time()
def plotbrightest(d, tid=None, tof=None):
    '''
    Plots current time of flight data from one shot.
    Updates _tofplot window
    Input:
        image data
    Output:
        None, updates plot window
    '''

    imagehist(d)
    tofhist(tof)
    brightnesshist(np.mean(d)-np.mean(imagehist.average))
    tofsignalhist(np.mean(tof)) # need something more elaborate here, e.g. roi sum
    tidhist(tid)

    # just some timing info
    now = time()
    global lastTime   # sorry for the dirty code :/
    dt = now - lastTime
    lastTime = now
    fps =1.0/dt
      


    _pgstatimg.plot(brightnesshist.data, clear=True, title = 'statistics mcp signal')
    _pgstattof.plot(-tofsignalhist.data, clear=True, title = 'statistics tof signal')
    _pgstattof.setTitle('%0.2f fps' % fps)
    ######_pgimage2.setImage(d-imagehist.average, autoRange=False)
    idx = np.argmax(brightnesshist[-brightestlen:])
    global _brightlasttid  # This line REALLY hurts :/
    if tidhist[-brightestlen:][idx] != _brightlasttid:
        print('new brightest shot: {:9} -> {:9}'.format(_brightlasttid, tid))
        #####_pgbrightestimg.setImage(imagehist[idx])
        #print('update')
        _brightlasttid = tidhist[-brightestlen:][idx]
        _pgbrightestimgtof.plot(-tofhist[idx].reshape((tofhist[idx].size,)), clear=True, title='tof for brigtest image')
        img_data=imagehist[idx]-imagehist.average
        actimgitem=pg.ImageItem(img_data) #, title = 'brightest image'
        actimgitem.setLevels([0,img_data.max()])
        _pgbrightestimg.addItem(actimgitem)

    #print(np.mean(imagehist[idx]))
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
    #ds = xfel.getImage(ds)
    ds = xfel.getImageandTof(ds)
    for data in ds:
        #plotimage(image)
        plotbrightest(data['image'], tid=data['tid'], tof=data['tof'])


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








