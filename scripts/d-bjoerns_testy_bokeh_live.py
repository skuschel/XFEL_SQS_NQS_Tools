import time
import numpy as np
import holoviews as hv

import datashader as ds
from holoviews.operation.datashader import datashade

from holoviews import opts
from holoviews.streams import Pipe, RangeXY, PlotSize
import holoviews.plotting.bokeh

from tornado import gen

import sqs_nqs_tools.online as online
import sqs_nqs_tools as tools

hv.extension('bokeh')
renderer = hv.renderer('bokeh')
hv.output(dpi=300, size=100)

#default Data
N=10000
N_datapts = N
x = np.arange(N)
y = np.random.rand(N)

pipe2 = Pipe(data=[])
#pipe3 = Pipe(data=[])
#TOF_dmap = hv.DynamicMap(hv.Curve, streams=[pipe2])
TOF_dmap = hv.DynamicMap(hv.Curve, streams=[pipe2])
#TOF_dmap = hv.DynamicMap(hv.Curve((x,y)))
#TOF_dmap.opts(xlim=(0, 1000),ylim=(-1, 1))


#TOF_dmap_opt = datashade(TOF_dmap, streams=[hv.streams.RangeXY])
TOF_dmap_opt = datashade(TOF_dmap, streams=[PlotSize, RangeXY], dynamic=True)
layout = TOF_dmap_opt.opts(width=1500,height=900,xlim=(0, N),ylim=(-500, 40))

@gen.coroutine
def update_pipe(x,y):
    pipe2.send((x,y))

@online.pipeline
def foldTofs(d):
    '''
    fold all the tofs from a train into a singal tof
    '''



    d['tof'] = d['tof'][130000:130000+N_datapts]
    return d

@gen.coroutine
def makeBigData():
    source = 'tcp://10.253.0.142:6666'
    source = 'tcp://127.0.0.1:8001'
    ds = online.servedata(source) #get the datastream
    ds = online.getTof(ds) #get the tofs
    ds = foldTofs(ds)
    #print("get some detector")
    #ds = online.getSomeDetector(ds, name='tid', spec0='SQS_DIGITIZER_UTC1/ADC/1:network', spec1='digitizers.trainId')
    print("done")

    for data in ds:
        print("ds ...")
        x = np.arange(N_datapts); y = np.squeeze(data['tof'])
        t_0 = time.time()
        #time.sleep(0.1)
        yield gen.sleep(0.01)
        #y = np.random.rand(N)
        t_1 = time.time()
        update_pipe(x,y)
        #pipe3.send(([time.time()-t_0]))
        print([round(1/(time.time()-t_0),1), round(1/(time.time()-t_1),1)])

doc = renderer.server_doc(layout)
doc.title = 'HoloViews App'

makeBigData()
#thread = Thread(target=makeBigData)
#thread.start()
