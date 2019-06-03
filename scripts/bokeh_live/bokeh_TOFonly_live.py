# IMPORT MODULES
import time
import numpy as np
import pandas as pd
import holoviews as hv
import datashader as ds
from holoviews.operation.datashader import datashade, rasterize
from holoviews.operation import decimate

from holoviews import opts
from holoviews.streams import Pipe, RangeXY, PlotSize, Buffer
import holoviews.plotting.bokeh
from tornado import gen
import tornado
from scipy.misc import imresize
from scipy import signal

from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
from bokeh.document import without_document_lock
from bokeh.models.widgets import Button
from functools import partial

from threading import Thread

import sqs_nqs_tools.online as online
from sqs_nqs_tools.online.bokeh import performanceMonitor
import sqs_nqs_tools.online.bokeh as sqs_bk
import sqs_nqs_tools as tools

# MODULE CONFIGS
hv.extension('bokeh')
renderer = hv.renderer('bokeh')  # renderer to convert objects from holoviews to bokeh
renderer = renderer.instance(mode="server")
hv.output(dpi=300, size=100)
doc = curdoc()  # DOC for Bokeh Objects

# DATA SOURCE
source = 'tcp://10.253.0.142:6666'  # LIVE
#source = 'tcp://127.0.0.1:8011' # emulated live

# DATA CONFIG
N_datapts = 35000 # total number of TOF datapoints that are visualized
start_tof = 485000 # index of first TOF datapoint considered
## yielded config values
end_tof = start_tof+N_datapts # index of last TOF datapoint considered
x_tof = np.arange(start_tof,end_tof) # x-axis for tof data points

makeBigData_stop = False

# Data handling functions

@online.pipeline
def processTofs(d):
    '''
    process tofs in pipeline
    '''
    d['tof'] = d['tof'][start_tof:end_tof] # cut out index range that we are interested in
    d['x_tof'] = x_tof # add values for x axis
    return d

def makeDatastreamPipeline(source):
    ds = online.servedata(source) #get the datastream
    ds = online.getTof(ds) #get the tofs
    ds = processTofs(ds) #treat the tofs
    ds = online.getSomeDetector(ds, name='tid', spec0='SQS_DIGITIZER_UTC1/ADC/1:network', spec1='digitizers.trainId') #get current trainids from digitizer property
    return ds

def makeBigData():
    print("Source: "+ source) # print source set for data
    # Setup Data Stream Pipeline
    ds = makeDatastreamPipeline(source)
    # Initialize performance monitor
    perf = performanceMonitor() # outputs to console info on performance - eg what fraction of data was not pulled from live stream and thus missed
    n=-1
    print("Start Live Display")
    for data in ds:
        n+=1
        data['tid']=n # just for testing
        # performance monitor - frequency of displaying data + loop duration
        perf.iteration()
        # Things for add next tick callback
        if n%10 is not 0:
            callback_data_dict = dict()
            callback_data_dict["tof_trace"] = ( np.squeeze(data['x_tof']) , np.squeeze(data['tof']))

            buffer_or_pipe_dict = dict()
            buffer_or_pipe_dict["tof_trace"] = _pipe__TOF_single

            if 'all_updates_next_tick_callback' in locals():
                if all_updates_next_tick_callback in doc.session_callbacks:
                    doc.remove_next_tick_callback(all_updates_next_tick_callback)
            all_updates_next_tick_callback = callback_data_dict_into_callback(buffer_or_pipe_dict, callback_data_dict, n )

        # Things for performance analysis
        perf.update_trainId(str(data['tid'])) # give current train id to performance monitor for finding skipping of shots
        perf.time_for_loop_step() # tell performance monitor that this is the end of the for loop




def callback_data_dict_into_callback( buffer_or_pipe_dict, callback_data_dict, n ):
    next_tick_callback = doc.add_next_tick_callback(partial(updateAllPlotPipes,buffer_or_pipe_dict,callback_data_dict, n))
    return next_tick_callback

@without_document_lock
def updateAllPlotPipes(buffer_or_pipe_dict, callback_data_dict, n):
    print("#####  "+str(n)+"  ######## Update all Plots Func @ n = "+ str(n))
    for key in buffer_or_pipe_dict:
        if key is not "pnCCD_recent_hits":
            buffer_or_pipe_dict[key].send(callback_data_dict[key])
        else:
            fill_recent_hits_pipes(buffer_or_pipe_dict[key],callback_data_dict[key], n)
    print(">>>>>>>  "+str(n)+"  <<<<<< Update all Plots Func @ n = "+ str(n))
    pass

@without_document_lock
def fill_recent_hits_pipes(buffer_or_pipe_list,data, n):
    for i in range(len(buffer_or_pipe_list)):
        buffer_or_pipe_list[i].send(data[-i,:,:])

# plot tools functions
def largeData_line_plot(pipe_or_buffer, width=1500, height=400,ylim=(-500, 40),xlim=(start_tof,start_tof+N_datapts), xlabel="index", ylabel="TOF signal", cmap = ['blue'], title=None):
    TOF_dmap = hv.DynamicMap(hv.Curve, streams=[pipe_or_buffer])
    TOF_dmap_opt = datashade(TOF_dmap, streams=[PlotSize, RangeXY], dynamic=True, cmap = cmap)
    return sqs_bk.hv_to_bokeh_obj( TOF_dmap_opt.opts(width=width,height=height,ylim=ylim,xlim=xlim, xlabel=xlabel, ylabel=ylabel, title = title), renderer) 

def smallData_line_plot(pipe_or_buffer, width=1500, height=400,ylim=(-500, 40),xlim=(start_tof,start_tof+N_datapts), xlabel="index", ylabel="TOF signal", title=None):
    TOF_dmap = hv.DynamicMap(hv.Curve, streams=[pipe_or_buffer]).redim.range().opts( norm=dict(framewise=True) ) #.redim.range().opts( norm=dict(framewise=True) ) makes x and y lim dynamic
    return sqs_bk.hv_to_bokeh_obj( TOF_dmap.opts(width=width,height=height,ylim=ylim,xlim=xlim, xlabel=xlabel, ylabel=ylabel, title = title), renderer)

def start_stop_dataThread():
    global makeBigData_stop
    if not makeBigData_stop:
        makeBigData_stop = True
    else:
        thread.start()

# Data buffers for live stream
print("...2")

# Data pipes and buffers for plots
## pipes provide a full update of data to the underlying object eg. plot
## buffers add only a single value to the plot and may kick one out when number of elements in the buffer has reached the length/size of the buffer
_pipe__TOF_single = Pipe(data=[])

# SETUP PLOTS
print("...3")
# example for coupled plots
#         layout = hv.Layout(largeData_line_plot(_pipe__TOF_single, title="TOF single shots - LIVE") + largeData_line_plot(_pipe__TOF_single, title="TOF single shots - LIVE 2", cmap=['red'])).cols(1)
## TOF
bokeh_live_tof =  largeData_line_plot(_pipe__TOF_single, title="TOF single shots - LIVE", width = 1900, height=900)
## SET UP Additional Widgets
bokeh_button_StartStop = Button(label = "Start / Stop", button_type="success")
bokeh_button_StartStop.on_click(start_stop_dataThread)
# SET UP BOKEH LAYOUT
#
bokeh_row_1 = row(bokeh_live_tof)
bokeh_row_interact  = bokeh_button_StartStop
bokeh_layout = column(bokeh_row_1, bokeh_row_interact)
print("...4")
# add bokeh layout to current doc
doc.add_root(bokeh_layout)
print("...5")
# Start Thread for Handling of the Live Data Strem
thread = Thread(target=makeBigData)
thread.start()
