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

import numpy as np
import pandas as pd
import holoviews as hv
from holoviews import dim, opts

hv.extension('bokeh')

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
def makeSomeData():
    source = 'tcp://10.253.0.142:6666'
    source = 'tcp://127.0.0.1:8001'
    ds = online.servedata(source) #get the datastream
    ds = online.getTof(ds) #get the tofs
    print("get some detector")
    ds = online.getSomeDetector(ds, name='tid', spec0='SQS_DIGITIZER_UTC1/ADC/1:network', spec1='digitizers.channel_1_A.apd.pulseId')
    print("done")
    # initialize variables for performance monitoring
    t_start = 0
    for_loop_step_dur = 0
    # start with for loop
    print("Start With For Loop")
    for data in ds:
	# performance monitor - frequency of displaying data + loop duration
        print("Frequency: "+str(round(1/(time.time()-t_start),2))+ " Hz  |  Loop duration vs allowed duration: "+str(round(for_loop_step_dur/0.1*100,1))+ " % (OK if <100%)") 
        t_start = time.time()
        
        # extract TOF data
        tof = data['tof']
        tof = tof[200000:200000+N_datapts]
        # print(tof.shape)    # just in case debugging because of shape errors
        N_samples = len(tof)
        x = np.arange(N_samples); y = np.squeeze(tof)
        
        # Train ID Data
        trainId = str(data['tid'])
        
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
