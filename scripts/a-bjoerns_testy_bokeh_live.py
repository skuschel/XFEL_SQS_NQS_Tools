#!/usr/bin/env python3

# IMPORT
## general
import numpy as np
from math import pi
import time

## SQS
import sqs_nqs_tools.online as online
import sqs_nqs_tools as tools

## bokeh for plotting
from bokeh.layouts import column, row
from bokeh.models import Button, ColumnDataSource
from bokeh.models.widgets import Div
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc
from functools import partial
from threading import Thread
from tornado import gen

#import numpy as np
#import pandas as pd
#import holoviews as hv
#from holoviews import dim, opts

#hv.extension('bokeh')

## just for sample code
from random import random

print("i")
N_datapts = 100000
print("i")
# Setup Data Source for Live Updates
d_src_tof = ColumnDataSource(data=dict(x=np.zeros(N_datapts), y=np.zeros(N_datapts)))#, tid='init'))
d_src_text = ColumnDataSource(data=dict(tid=['init']))
print("i")
# Setup Plots
## TOF Live
p = figure(x_range=[0,N_datapts], y_range=[-400,30], plot_width=1200, plot_height=400)
l = p.line(x='x', y='y', source=d_src_tof)
## Train ID Display
def trainId_to_html(trainID):
    return '<span style="font-size:30pt">'+str(trainID)+'</span>'
div_trainId = Div(text='tid',width=200, height=100)
#div_trainId = Div(text='tid', source=d_src_text,width=200, height=100)
print("i")
# Define current document
doc = curdoc()
print("i")
# Update Plots Routine
@gen.coroutine
def update(x,y,tid):
    patches_tof = {'x' : [ (slice(N_datapts),x) ], 'y' : [ (slice(N_datapts),y) ]}
    patches_text = { 'tid' : [(0,tid)] }
    d_src_tof.patch(patches_tof)
    #d_src_text.patch(patches_text)

# Function That waits for and processes the live data  
@online.pipeline 
def foldTofs(d):
    '''
    fold all the tofs from a train into a singal tof
    '''
    
   
   
    d['tof'] = d['tof'][200000:200000+N_datapts]
    return d
    
def makeSomeData():
    source = 'tcp://10.253.0.142:6666'
    #source = 'tcp://127.0.0.1:8001'
    ds = online.servedata(source) #get the datastream
    ds = online.getTof(ds) #get the tofs
    ds = foldTofs(ds)
    print("get some detector")
    ds = online.getSomeDetector(ds, name='tid', spec0='SQS_DIGITIZER_UTC1/ADC/1:network', spec1='digitizers.trainId')
    print("done")
    # initialize variables for performance monitoring
    t_start = time.time()
    for_loop_step_dur = 0
    n=-1
    freq_avg = 0
    dt_avg = 0
    trainId = 0
    trainId_old = -1
    skip_count = 0
    # start with for loop
    print("Start With For Loop")
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
            print("Frequency: "+str(round(freq_avg,2)) +" Hz  |  skipped: "+str(skip_count)+" ( "+str(round(skip_count/n*100,1))+" %)  |  n: "+str(n)+"/"+str(trainId)+"  |  Loop benchmark: "+str(round(loop_classification_percent,1))+ " % (OK if <100%) - "+loop_classification_msg) 
        
        t_1 = time.time()
        # extract TOF data
        #tof = data['tof']
        t_2 = time.time()
        #tof = tof[200000:200000+N_datapts]
        # print(tof.shape)    # just in case debugging because of shape errors
        #N_samples = len(tof)
        #print(data['tof'].shape)
        x = np.arange(N_datapts); y = np.squeeze(data['tof'])
        t_3 = time.time()
        
        # Train ID Data
        trainId_old = trainId
        trainId = str(data['tid'])
        if int(trainId) - int(trainId_old) is not 1:
            #print('SKIP')
            skip_count +=1
        
        # update from callback
        doc.add_next_tick_callback(partial(update, x=x, y=y,tid=trainId))
        
        # monitor for loop step duration
        for_loop_step_dur = time.time()-t_start

# Assemble Document        
doc.add_root(row(p,div_trainId))

# Start Thread for Live Data
thread = Thread(target=makeSomeData)
thread.start()



###### ----------- END OF CODE ----------- ######




# this was the first testing script that worked
'''
# First Testing Script --> Worked
# prepare
## plot
p = figure(x_range=(0,100), y_range=(0,100), toolbar_location=None)
p.border_fill_color = 'black'
p.background_fill_color = 'black'
p.outline_line_color = None
p.grid.grid_line_color = None

r = p.text(x=[], y=[], text=[], text_color=[], text_font_size="20pt", text_baseline="middle", text_align="center")
i=0

dsrc = r.data_source

# callback
def callback():
    global i
    
    new_data = dict()
    new_data['x'] = dsrc.data['x'] + [random()*70+15]
    new_data['y'] = dsrc.data['y'] + [random()*70+15]
    new_data['text_color'] = dsrc.data['text_color'] + [RdYlBu3[i%3]]
    new_data['text'] = dsrc.data['text'] + [str(i)]
    dsrc.data = new_data
    
    i += 1
    
# further UI elements
button = Button(label='Press me')
button.on_click(callback)

# add UI elements to UI
curdoc().add_root(column(button,p))
'''
