import time
import numpy as np
import holoviews as hv
import datashader as ds
from holoviews.operation.datashader import datashade

from holoviews import opts
from holoviews.streams import Pipe, RangeXY, PlotSize
import holoviews.plotting.bokeh
from tornado import gen

from bokeh.plotting import figure, curdoc
from functools import partial

from threading import Thread

import sqs_nqs_tools.online as online
import sqs_nqs_tools as tools





hv.extension('bokeh')
renderer = hv.renderer('bokeh')
hv.output(dpi=300, size=100)

#default Data
N=400000
N_datapts = N
x = np.arange(N)
y = np.random.rand(N)

start_tof = 130000
end_tof = start_tof+N_datapts
x_tof = np.arange(start_tof,end_tof)

pipe2 = Pipe(data=[])
TOF_dmap = hv.DynamicMap(hv.Curve, streams=[pipe2])
TOF_dmap2 = hv.DynamicMap(hv.Scatter, streams=[pipe2])

TOF_dmap_opt = datashade(TOF_dmap, streams=[PlotSize, RangeXY], dynamic=True, cmap = ['blue'])
TOF_dmap_opt2 = datashade(TOF_dmap2, streams=[PlotSize, RangeXY], dynamic=True, cmap = ['red'])
layout = TOF_dmap_opt.opts(width=1500,height=800,ylim=(-500, 40),xlim=(130000,130000+N_datapts)) + TOF_dmap_opt2.opts(width=400,height=400,ylim=(-500, 40),xlim=(130000,130000+N_datapts))

doc = curdoc()

@gen.coroutine
def update_pipe(x,y):
    pipe2.send((x,y))

@online.pipeline
def foldTofs(d):
    '''
    fold all the tofs from a train into a singal tof
    '''
    
    d['tof'] = d['tof'][start_tof:end_tof]
    d['x_tof'] = x_tof
    return d

def makeBigData():
    source = 'tcp://10.253.0.142:6666'
    source = 'tcp://127.0.0.1:8011'
    print("Source: "+ source)
    print("Build Pipeline: Start")
    ds = online.servedata(source) #get the datastream
    ds = online.getTof(ds) #get the tofs
    ds = foldTofs(ds)
    print("get train id from digitzer")
    ds = online.getSomeDetector(ds, name='tid', spec0='SQS_DIGITIZER_UTC1/ADC/1:network', spec1='digitizers.trainId')
    print("Build Pipeline: Done")
    
    # initialize variables for performance monitoring
    t_start = time.time()
    for_loop_step_dur = 0
    n=-1
    freq_avg = 0
    dt_avg = 0
    trainId = 0
    trainId_old = -1
    skip_count = 0
    
    for data in ds:
        # performance monitor - frequency of displaying data + loop duration
        n+=1
        dt = (time.time()-t_start)
        t_start = time.time()
        freq = 1/dt
        if n>0:
            dt_avg = (dt_avg * (n-1) + dt) / n
            freq_avg = 1/dt_avg
            loop_classification_percent = for_loop_step_dur/0.1*100
            if loop_classification_percent < 100:
                loop_classification_msg="OK"
            else:
                loop_classification_msg="TOO LONG!!!"
            print("Frequency: "+str(round(freq_avg,1)) +" Hz  |  skipped: "+str(skip_count)+" ( "+str(round(skip_count/n*100,1))+" %)  |  n: "+str(n)+"/"+str(trainId)+"  |  Loop benchmark: "+str(round(loop_classification_percent,1))+ " % (OK if <100%) - "+loop_classification_msg) 
        
        #TOF
        t_start_loop = time.time()
        x = np.squeeze(data['x_tof']); y = np.squeeze(data['tof'])
        doc.add_next_tick_callback(partial(update_pipe, x=x, y=y))
        #TrainId
        trainId_old = trainId
        trainId = str(data['tid'])
        # monitor for loop step duration
        for_loop_step_dur = time.time()-t_start_loop
        #Monitor Train ID skipping
        if n == 0:
            trainId_old = str(int(trainId) -1)
        if int(trainId) - int(trainId_old) is not 1:
            skip_count +=1
        

        

#doc = renderer.server_doc(layout)
renderer = renderer.instance(mode="server")
hvplot = renderer.get_plot(layout)  

doc.add_root(hvplot.state)

#doc.title = 'HoloViews App'

print("Let's make some data")
#makeBigData()
thread = Thread(target=makeBigData)
thread.start()
