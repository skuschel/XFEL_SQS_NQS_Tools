#!/usr/bin/env python3

# Stephan Kuschel, Matt Ware, Catherine Saladrigas, Christian Peltz 2019

import numpy as np
import pyqtgraph as pg
import sqs_nqs_tools.online as xfel
import sqs_nqs_tools as tools
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

win_gallery = pg.GraphicsWindow()
_pggaltof_0 = win_gallery.addPlot(row = 0, col = 0)
_pggalimg_0 = win_gallery.addViewBox(row = 1, col = 0)
_pggaltof_1 = win_gallery.addPlot(row = 0, col = 1)
_pggalimg_1 = win_gallery.addViewBox(row = 1, col = 1)
_pggaltof_2 = win_gallery.addPlot(row = 0, col = 2)
_pggalimg_2 = win_gallery.addViewBox(row = 1, col = 2)
_pggaltof_3 = win_gallery.addPlot(row = 0, col = 3)
_pggalimg_3 = win_gallery.addViewBox(row = 1, col = 3)

#fakedata = np.random.rand(100,)
#fakeimgdata  = np.random.rand(100,100)
#fakeimgitem0=pg.ImageItem(fakeimgdata) #, title = 'brightest image'
#fakeimgitem1=pg.ImageItem(fakeimgdata) #, title = 'brightest image'
#fakeimgitem2=pg.ImageItem(fakeimgdata) #, title = 'brightest image'
#fakeimgitem3=pg.ImageItem(fakeimgdata) #, title = 'brightest image'
#_pggalimg_0.addItem(fakeimgitem0)
#_pggalimg_1.addItem(fakeimgitem1)
#_pggalimg_2.addItem(fakeimgitem2)
#_pggalimg_3.addItem(fakeimgitem3)
#_pggaltof_0.plot(fakedata, clear=True, title = 'statistics mcp signal')
#_pggaltof_1.plot(fakedata, clear=True, title = 'statistics mcp signal')
#_pggaltof_2.plot(fakedata, clear=True, title = 'statistics mcp signal')
#_pggaltof_3.plot(fakedata, clear=True, title = 'statistics mcp signal')

####_pgbrightestimg = pg.image(title='Brightest Shots {}'.format(xfel.__version__))
brightestlen = 15
imagehist = tools.DataBuffer(brightestlen)
tofhist = tools.DataBuffer(brightestlen)
tidhist = tools.DataBuffer(brightestlen)
brightnesshist = tools.DataBuffer(300)
tofsignalhist = tools.DataBuffer(300)
_brightlasttid = -1
_numbergoodshots = -1
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
    act_brightness=np.mean(d)-np.mean(imagehist.average)
    brightnesshist(act_brightness)
    tofsignalhist(np.mean(tof[5800:7800])) # need something more elaborate here, e.g. roi sum
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
    global _numbergoodshots  # This line REALLY hurts :/
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
        
    brightness_threshold=10
    #if act_brightness>10:
    if act_brightness>brightness_threshold:
        _numbergoodshots+=1
        plot_id=np.mod(_numbergoodshots,4)
        if plot_id == 0:
             _pggaltof_0.plot(-tofhist[idx].reshape((tofhist[idx].size,)), clear=True)
             galimgitem=pg.ImageItem(img_data) #, title = 'brightest image'
             _pggalimg_0.addItem(galimgitem)
        elif plot_id == 1:
             _pggaltof_1.plot(-tofhist[idx].reshape((tofhist[idx].size,)), clear=True)
             galimgitem=pg.ImageItem(img_data) #, title = 'brightest image'
             _pggalimg_1.addItem(galimgitem)
        elif plot_id == 2:
             _pggaltof_2.plot(-tofhist[idx].reshape((tofhist[idx].size,)), clear=True)
             galimgitem=pg.ImageItem(img_data) #, title = 'brightest image'
             _pggalimg_2.addItem(galimgitem)
        else:
             _pggaltof_3.plot(-tofhist[idx].reshape((tofhist[idx].size,)), clear=True)
             galimgitem=pg.ImageItem(img_data) #, title = 'brightest image'
             _pggalimg_3.addItem(galimgitem)


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








