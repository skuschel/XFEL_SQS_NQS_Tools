#!/usr/bin/env python3

# Stephan Kuschel, 2019

import numpy as np
import pyqtgraph as pg



def servedata(host, type='REQ'):
    from karabo_bridge import Client
    c = Client(host, type)
    for ret in c:
    	yield ret



_tofplot = pg.plot(title='ToF')
def plottof(data):
    d = data['SQS_DIGITIZER_UTC1/ADC/1:network']['digitizers.channel_1_A.raw.samples']
    #print(d.shape)
    _tofplot.plot(d, clear=True)
    pg.QtGui.QApplication.processEvents()



def main(source):
    for data, meta in servedata(source):
        plottof(data)




if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    default='tcp://127.0.0.1:9898'
    parser.add_argument('source', type=str, help='the source of the data stream. Default is "{}"'.format(default),
            default=default, nargs='?')
    args = parser.parse_args()
    main(args.source)








