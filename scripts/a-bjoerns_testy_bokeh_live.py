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
from bokeh.layouts import column
from bokeh.models import Button, ColumnDataSource
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc
from functools import partial
from threading import Thread
from tornado import gen

## just for sample code
from random import random

#N_datapts = 10000
N_datapts = 10000

d_src = ColumnDataSource(data=dict(x=np.zeros(N_datapts), y=np.zeros(N_datapts)))

doc = curdoc()

@gen.coroutine
def update(x,y):
    patches = {'x' : [ (slice(N_datapts),x) ], 'y' : [ (slice(N_datapts),y) ] }
    d_src.patch(patches)
    
def makeSomeData():
    source = 'tcp://10.253.0.142:6666'
    ds = online.servedata(source) #get the datastream
    ds = online.getTof(ds) #get the tofs
    
    for data in ds: 
        t_start = time.time()
        
        tof = data['tof']
        tof = tof[200000:200000+N_datapts]
        print(tof.shape)
        N_samples = len(tof)
        x = np.arange(N_samples); y = np.squeeze(tof)
        
        #print("T1 = "+str(time.time()-t_start))
        # update from callback
        doc.add_next_tick_callback(partial(update, x=x, y=y))
        print("T2 = "+str(time.time()-t_start))
        
p = figure(x_range=[0,N_datapts], y_range=[-400,0])
l = p.line(x='x', y='y', source=d_src)

doc.add_root(p)
thread = Thread(target=makeSomeData)
thread.start()



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
