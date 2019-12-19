# IMPORT MODULES
import time
import numpy as np
import pandas as pd
import holoviews as hv
import datashader as ds
import colorcet as cc
from holoviews.operation.datashader import datashade, rasterize
from holoviews.operation import decimate

from holoviews import opts
from holoviews.streams import Pipe, RangeXY, PlotSize, Buffer, Stream
import holoviews.plotting.bokeh
from holoviews.plotting.util import process_cmap
from tornado import gen
import tornado
from scipy.misc import imresize
from scipy import signal

from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
from bokeh.document import without_document_lock
from bokeh.models.widgets import Button, Paragraph, Div
from functools import partial

from threading import Thread
import threader
import sqs_nqs_tools.online as online
import sqs_nqs_tools.online.bokeh as online_bokeh
import sqs_nqs_tools as tools

# MODULE CONFIGS
hv.extension('bokeh')
renderer = hv.renderer('bokeh')  # renderer to convert objects from holoviews to bokeh
renderer = renderer.instance(mode="server")
hv.output(dpi=300, size=100)
doc = curdoc()  # DOC for Bokeh Objects

# DATA SOURCE
source = 'tcp://10.253.0.142:6666'  # LIVE
#~ source = 'tcp://127.0.0.1:8010' # emulated live
tof_in_stream = True
pnCCD_in_stream = True
gmd_in_stream = True

two_monitors = False

img_downscale = 30
#~ colormap_pnCCD = 'Plasma'
#~ colormap_pnCCD = process_cmap('rainbow',provider='colorcet')
colormap_pnCCD = process_cmap('jet',provider='matplotlib')
pnCCD_color_lower_z_lim = 0.02 #0.02
pnCCD_color_upper_z_lim = 16 #5
pnCCDavg_color_lower_z_lim = 0.005 #0.005
pnCCDavg_color_upper_z_lim = 16 #2

makeBigData_stop = False
# DATA CONFIG
N_datapts = 31000 # total number of TOF datapoints that are visualized
start_tof = 59000 # index of first TOF datapoint considered
single_photon_adu = 250
background_pnCCD = np.zeros(shape=(1024,1024))
background_max_pnCCD = np.zeros(shape=(1024,1024))
dark_pnCCD = np.zeros(shape=(1024,1024))
get_background_pnCCD = False
get_background_max_pnCCD = False
get_dark_pnCCD = False
pnCCD_integral_hit_threshold = 1e7# 1.5e5
background_single_photon_adu = 250
if get_background_pnCCD:
    background_pnCCD = np.load('background_pnCCD.npy')
if get_dark_pnCCD:
    dark_pnCCD = np.load('dark_pnCCD.npy') / 16
if get_background_max_pnCCD:
    background_max_pnCCD = np.load('background_max_pnCCD.npy')
## yielded config values
end_tof = start_tof+N_datapts # index of last TOF datapoint considered
x_tof = np.arange(start_tof,end_tof) # x-axis for tof data points

# Data handling functions
@gen.coroutine
def update_pipe(x,y,pipe):
    pipe.send((x,y))

@online.pipeline
def processTofs(d):
    '''
    process tofs in pipeline
    '''
    #~ d['tof'] = d['tof'][start_tof:end_tof] # cut out index range that we are interested in
    d['x_tof'] = x_tof # add values for x axis
    if False:
        data = d['tof'] 
        samples = 16
        bg=[0,5000]
        for idx in range(samples):
            data_idx_selection = np.arange(idx,N_datapts,samples)
            data_excerpt = data[data_idx_selection]
            if bg is not None:
                data_excerpt = data_excerpt - np.mean(data_excerpt[int(np.floor(bg[0]/samples)):int(np.floor(bg[1]/samples))])
            data[data_idx_selection] = data_excerpt
        d['tof'] = data
    return d

@online.pipeline
def processPnCCDs(d):
    d['pnCCD'] = np.squeeze(d['pnCCD']) / single_photon_adu
    #~ d['pnCCD'] = d['pnCCD'] + 10
    #~ d['pnCCD'] = d['pnCCD'][256:768,256:768]
    #~ d['pnCCD'] = d['pnCCD'][420:600,420:600]
    return d

def makeDatastreamPipeline(source):
    ds = online.servedata(source) #get the datastream
    if pnCCD_in_stream:
        ds = online.getSomePnCCD(ds, name='pnCCD', spec0='SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output', spec1='data.image') #get pnCCD
        ds = online.getSomeDetector(ds, name='tid', spec0='SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output', spec1='timestamp.tid', readFromMeta=True) #get current trainids from gmd property
        ds = processPnCCDs(ds) # convert pnccd adu to photon count
    if gmd_in_stream:
        ds = online.getSomeDetector(ds, name='gmd', spec0='SA3_XTD10_XGM/XGM/DOOCS:output', spec1='data.intensitySa3TD') #get GMD
        #~ ds = online.getSomeDetector(ds, name='gmd_x', spec0='SA3_XTD10_XGM/XGM/DOOCS:output', spec1='data.xSa3TD') #get GMD
        #~ ds = online.getSomeDetector(ds, name='gmd_y', spec0='SA3_XTD10_XGM/XGM/DOOCS:output', spec1='data.ySa3TD') #get GMD
        #~ ds = online.getSomeDetector(ds, name='tid', spec0='SA3_XTD10_XGM/XGM/DOOCS:output', spec1='timestamp.tid', readFromMeta=True) 
    return ds


class makeBigDataThread(Thread):
    def run(self):
        makeBigData()
        
    def end(self):
        if self.is_alive():
            threader.killThread(self.ident)


def makeBigData():
    print("Source: "+ source) # print source set for data

    # Setup Data Stream Pipeline
    ds = makeDatastreamPipeline(source)
    perf = online_bokeh.performanceMonitor() # outputs to console info on performance - eg what fraction of data was not pulled from live stream and thus missed
    #print
    n=-1
    print("Start Live Display")
    for data in ds:
        n+=1
        # performance monitor - frequency of displaying data + loop duration
        perf.iteration()
        if data['pnCCD_in_data']: ## skip analysis if now pn ccd in data
            xgm_mean_1 = 1
            xgm_mean_2 = 1
            xgm_single = 1
            if gmd_in_stream:
                _SQSbuffer__GMD_history(data['gmd'][0])
                _SQSbuffer__xgm_mean_helper_1(data['gmd'][0])
                _SQSbuffer__xgm_mean_helper_2(data['gmd'][0])
                xgm_single = data['gmd'][0]
                xgm_mean_1 = np.mean(_SQSbuffer__xgm_mean_helper_1,axis=0) # current average 1
                xgm_mean_2 = np.mean(_SQSbuffer__xgm_mean_helper_2,axis=0) # current average 2
            if pnCCD_in_stream:
                pnCCD_single = np.squeeze(data['pnCCD']) # single shot
                _SQSbuffer__pnCCD_mean_helper_1(pnCCD_single) # average buffer 1 fill with new shot
                _SQSbuffer__pnCCD_mean_helper_2(pnCCD_single) # average buffer 2 fill with new shot
                pnCCD_mean_1 = np.mean(_SQSbuffer__pnCCD_mean_helper_1,axis=0) # current average 1
                pnCCD_mean_2 = np.mean(_SQSbuffer__pnCCD_mean_helper_2,axis=0) # current average 2
                pnCCD_integral_single =  np.sum(pnCCD_single) # integral single shot
                pnCCD_integral_mean =  np.sum(pnCCD_mean_1) # integral current average 1
                pnCCD_integral_mean_left = np.sum(pnCCD_mean_1[483:541,0:500])
                pnCCD_integral_mean_right = np.sum(pnCCD_mean_1[483:541,524:1023])
                pnCCD_integral_mean_bottom = np.sum(pnCCD_mean_1[524:1023,483:541])
                pnCCD_integral_mean_top = np.sum(pnCCD_mean_1[0:500,483:541])
                pnCCD_integral_mean_2 =  np.sum(pnCCD_mean_2) # integral current average 2
          
                _SQSbuffer__pnCCD_mean_1_integral(pnCCD_integral_mean)
                _SQSbuffer__pnCCD_mean_2_integral(pnCCD_integral_mean_2)
                _SQSbuffer__pnCCD_integral(pnCCD_integral_single)
                _SQSbuffer__pnCCD_mean_1_integral_proc(pnCCD_integral_mean/xgm_mean_1)
                _SQSbuffer__pnCCD_mean_1_integral_proc_top(pnCCD_integral_mean_top/xgm_mean_1)
                _SQSbuffer__pnCCD_mean_1_integral_proc_bottom(pnCCD_integral_mean_bottom/xgm_mean_1)
                _SQSbuffer__pnCCD_mean_1_integral_proc_right(pnCCD_integral_mean_right/xgm_mean_1)
                _SQSbuffer__pnCCD_mean_1_integral_proc_left(pnCCD_integral_mean_left/xgm_mean_1)
                _SQSbuffer__pnCCD_mean_2_integral_proc(pnCCD_integral_mean_2/xgm_mean_2)
                _SQSbuffer__pnCCD_integral_proc(pnCCD_integral_single/xgm_single)
                              
            _SQSbuffer__counter(n)
            now = time.time()
            _SQSbuffer__counter_time(now)
            ## TrainId
            trainId = str(data['tid'])
            # Things for add next tick callback
            if n%7==0: # skip plotting 
                # prepare for display
                pnCCD_single_display = pnCCD_single.copy()  # prepared single shot for display
                pnCCD_single_display[pnCCD_single_display<0.1] = 0.1  # prepared single shot for log scale
                pnCCD_mean_1_display = pnCCD_mean_1.copy()
                pnCCD_mean_1_display[pnCCD_mean_1_display<0.01] = 0.01 
                pnCCD_mean_2_display = pnCCD_mean_2.copy()
                pnCCD_mean_2_display[pnCCD_mean_2_display<0.01] = 0.01
                
                callback_data_dict = dict()
                callback_data_dict['OA_frequency_label'] = str(round(perf.freq_avg,1))
                if pnCCD_in_stream:
                    callback_data_dict["pnCCD_single"] = (pnCCD_single)
                    callback_data_dict["pnCCD_mean_1"] = (pnCCD_mean_1)
                    callback_data_dict["pnCCD_mean_2"] = (pnCCD_mean_2)
                    callback_data_dict["pnCCD_single_tid"] = (trainId)
                    callback_data_dict["pnCCD_integral"] = (_SQSbuffer__counter_time.data - now , _SQSbuffer__pnCCD_integral.data)
                    callback_data_dict["pnCCD_mean_1_integral"] = (_SQSbuffer__counter_time.data - now, _SQSbuffer__pnCCD_mean_1_integral.data)
                    callback_data_dict["pnCCD_mean_1_integral_proc_top"] = (_SQSbuffer__counter_time.data - now, _SQSbuffer__pnCCD_mean_1_integral_proc_top.data)
                    callback_data_dict["pnCCD_mean_1_integral_proc_bottom"] = (_SQSbuffer__counter_time.data - now, _SQSbuffer__pnCCD_mean_1_integral_proc_bottom.data)
                    callback_data_dict["pnCCD_mean_1_integral_proc_right"] = (_SQSbuffer__counter_time.data - now, _SQSbuffer__pnCCD_mean_1_integral_proc_right.data)
                    callback_data_dict["pnCCD_mean_1_integral_proc_left"] = (_SQSbuffer__counter_time.data - now, _SQSbuffer__pnCCD_mean_1_integral_proc_left.data)
                    callback_data_dict["pnCCD_mean_2_integral"] = (_SQSbuffer__counter_time.data - now, _SQSbuffer__pnCCD_mean_2_integral.data)
                    callback_data_dict["pnCCD_integral_proc"] = (_SQSbuffer__counter_time.data - now , _SQSbuffer__pnCCD_integral_proc.data )
                    callback_data_dict["pnCCD_mean_1_integral_proc"] = (_SQSbuffer__counter_time.data - now, _SQSbuffer__pnCCD_mean_1_integral_proc.data )
                    callback_data_dict["pnCCD_mean_2_integral_proc"] = (_SQSbuffer__counter_time.data - now, _SQSbuffer__pnCCD_mean_2_integral_proc.data  )
                    if False:
                        callback_data_dict["pnCCD_last_hit"] = last_hit_pnCCD
                        callback_data_dict["TOF_last_hit"] = ( np.squeeze(data['x_tof']) , np.squeeze(last_hit_TOF))
                        callback_data_dict["pnCCD_last_hit_tid"] = str(round((_SQSbuffer__trainId__last_hit.data[0])))
                if gmd_in_stream:
                    #~ callback_data_dict["pnCCD_last_hit_tid"] = 'XGM : '+str(round(data['gmd'][0],2))+" uJ"
                    callback_data_dict["gmd_history"] = ( _SQSbuffer__counter.data , _SQSbuffer__GMD_history.data )

                buffer_or_pipe_dict = dict()
                buffer_or_pipe_dict['OA_frequency_label'] = None
                if pnCCD_in_stream:
                    buffer_or_pipe_dict["pnCCD_single"] = _pipe__pnCCD_single
                    buffer_or_pipe_dict["pnCCD_mean_1"] = _pipe__pnCCD_mean_1
                    buffer_or_pipe_dict["pnCCD_mean_2"] = _pipe__pnCCD_mean_2
                    buffer_or_pipe_dict["pnCCD_single_tid"] = None
                    buffer_or_pipe_dict["pnCCD_integral"] = _pipe__pnCCD_integral
                    buffer_or_pipe_dict["pnCCD_mean_1_integral"] = _pipe__pnCCD_mean_1_integral
                    buffer_or_pipe_dict["pnCCD_mean_2_integral"] = _pipe__pnCCD_mean_2_integral
                    buffer_or_pipe_dict["pnCCD_integral_proc"] = _pipe__pnCCD_integral_by_gmd
                    buffer_or_pipe_dict["pnCCD_mean_1_integral_proc"] = _pipe__pnCCD_mean_1_integral_by_gmd
                    buffer_or_pipe_dict["pnCCD_mean_1_integral_proc_right"] = _pipe__pnCCD_mean_1_integral_by_gmd_right
                    buffer_or_pipe_dict["pnCCD_mean_1_integral_proc_left"] = _pipe__pnCCD_mean_1_integral_by_gmd_left
                    buffer_or_pipe_dict["pnCCD_mean_1_integral_proc_top"] = _pipe__pnCCD_mean_1_integral_by_gmd_top
                    buffer_or_pipe_dict["pnCCD_mean_1_integral_proc_bottom"] = _pipe__pnCCD_mean_1_integral_by_gmd_bottom
                    buffer_or_pipe_dict["pnCCD_mean_2_integral_proc"] = _pipe__pnCCD_mean_2_integral_by_gmd
                    if False:
                        hit_found = False
                        buffer_or_pipe_dict["pnCCD_last_hit"] = _pipe__pnCCD_hits__last_hit
                        buffer_or_pipe_dict["pnCCD_last_hit_tid"] = None
                        buffer_or_pipe_dict["TOF_last_hit"] = _pipe__TOF_hits__last_hit
                if gmd_in_stream:
                    #~ buffer_or_pipe_dict["pnCCD_last_hit_tid"] = None
                    buffer_or_pipe_dict["gmd_history"] = _pipe__GMD_history

                if 'all_updates_next_tick_callback' in locals():
                    if all_updates_next_tick_callback in doc.session_callbacks:
                        doc.remove_next_tick_callback(all_updates_next_tick_callback)
                all_updates_next_tick_callback = callback_data_dict_into_callback(buffer_or_pipe_dict, callback_data_dict, n )

            # Things for performance analysis
            

            perf.update_trainId(trainId) # give current train id to performance monitor for finding skipping of shots
        perf.time_for_loop_step() # tell performance monitor that this is the end of the for loop


# Helper to convert from holoviews to bokeh
def hv_to_bokeh_obj(hv_layout):
    # convert holoviews layout to bokeh object
    hv_plot = renderer.get_plot(hv_layout)
    return hv_plot.state

def pd_data_xy(x,y):
    # generates a pd dataframe (special data structure that holoviews likes) with x y data in the columns x and y
    return pd.DataFrame([(x,y)], columns=['x','y'])

def data_into_buffer_or_pipe(buffer_or_pipe, data,n):
    next_tick_callback = doc.add_next_tick_callback(partial(test_func,buffer_or_pipe,data,n))
    return next_tick_callback

def data_into_recent_hits_pipes(buffer_or_pipe_list, data,n):
    next_tick_callback = doc.add_next_tick_callback(partial(fill_recent_hits_pipes,buffer_or_pipe_list,data,n))
    return next_tick_callback

def callback_data_dict_into_callback( buffer_or_pipe_dict, callback_data_dict, n ):
    next_tick_callback = doc.add_next_tick_callback(partial(updateAllPlotPipes,buffer_or_pipe_dict,callback_data_dict, n))
    return next_tick_callback

@without_document_lock
def updateAllPlotPipes(buffer_or_pipe_dict, callback_data_dict, n):
    print("#####  "+str(n)+"  ######## Update all Plots Func @ n = "+ str(n))
    for key in buffer_or_pipe_dict:
        if key is 'pnCCD_single_tid':
            bokeh_pnccd_live_trainid_label.text = '<p><span style="font-size:20pt">Train ID: '+callback_data_dict[key]+'<span></p>'
            pass
        elif key is 'pnCCD_last_hit_tid':
            bokeh_last_hit_trainid_label.text = '<p><span style="font-size:20pt">Train ID: '+callback_data_dict[key]+'<span></p>'
            #~ hv_dmap_last_hit_pnCCD.title = callback_data_dict[key]
        elif key is 'OA_frequency_label':
            bokeh_daq_frequency_label.text = '<p><span style="font-size:20pt">Analysis Frequency: '+callback_data_dict[key]+' Hz<span></p>'
        elif key is 'pnCCD_recent_hits_tids':
            txt = '<p><span style="font-size:20pt">'
            for ids in callback_data_dict[key]:
                txt = txt + str(ids) + "<br>"
            txt = txt +'<span></p>'
            bokeh_buffer_last_hit_trainids.text=txt
            pass
        else:
            buffer_or_pipe_dict[key].send(callback_data_dict[key])
            
    print(">>>>>>>  "+str(n)+"  <<<<<< Update all Plots Func @ n = "+ str(n))
    pass
@without_document_lock
def test_func(buffer_or_pipe,data, n):
    print("Called Test Func @ n = "+ str(n))
    buffer_or_pipe.send(data)
@without_document_lock
def fill_recent_hits_pipes(buffer_or_pipe_list,data, n):
    for i in range(len(buffer_or_pipe_list)):
        buffer_or_pipe_list[i].send(data[-i,:,:])

def test_func_debug(buffer_or_pipe,data,n):
    print("Called Test Func Debug")
    print(data)
    buffer_or_pipe.send(data)
# plot tools functions
def largeData_line_plot(pipe_or_buffer, width=1500, height=400,ylim=(-500, 40),xlim=(start_tof,start_tof+N_datapts), xlabel="index", ylabel="TOF signal", cmap = ['blue'], title=None):
    TOF_dmap = hv.DynamicMap(hv.Curve, streams=[pipe_or_buffer])
    TOF_dmap_opt = datashade(TOF_dmap, streams=[PlotSize, RangeXY], dynamic=True, cmap = cmap)
    return hv_to_bokeh_obj( TOF_dmap_opt.opts(width=width,height=height,ylim=ylim,xlim=xlim, xlabel=xlabel, ylabel=ylabel, title = title) )

def smallData_line_plot(pipe_or_buffer, width=1500, height=400,ylim=(-500, 40),xlim=(start_tof,start_tof+N_datapts), xlabel="index", ylabel="", title=None):
    TOF_dmap = hv.DynamicMap(hv.Curve, streams=[pipe_or_buffer]).redim.range().opts( norm=dict(framewise=True) ) #.redim.range().opts( norm=dict(framewise=True) ) makes x and y lim dynamic
    return hv_to_bokeh_obj( TOF_dmap.opts(width=width,height=height,ylim=ylim,xlim=xlim, xlabel=xlabel, ylabel=ylabel, title = title))

def smallData_2line_plot(pipe_or_buffer_1,pipe_or_buffer_2, width=1500, height=400,ylim=(-500, 40),xlim=(start_tof,start_tof+N_datapts), xlabel="index", ylabel="", title=None):
    TOF_dmap_1 = hv.DynamicMap(hv.Curve, streams=[pipe_or_buffer_1]).redim.range().opts( norm=dict(framewise=True) ) #.redim.range().opts( norm=dict(framewise=True) ) makes x and y lim dynamic
    TOF_dmap_2 = hv.DynamicMap(hv.Curve, streams=[pipe_or_buffer_2]).redim.range().opts( norm=dict(framewise=True) ) #.redim.range().opts( norm=dict(framewise=True) ) makes x and y lim dynamic
    TOF_dmap = TOF_dmap_1 * TOF_dmap_2
    return hv_to_bokeh_obj( TOF_dmap.opts(width=width,height=height,ylim=ylim,xlim=xlim, xlabel=xlabel, ylabel=ylabel, title = title))

def smallData_scatter_plot(pipe_or_buffer, width=1500, height=400,ylim=(None, None),xlim=(start_tof,start_tof+N_datapts), xlabel="index", ylabel="", title=None):
    TOF_dmap = hv.DynamicMap(hv.Scatter, streams=[pipe_or_buffer]).redim.range().opts( norm=dict(framewise=True) ) #.redim.range().opts( norm=dict(framewise=True) ) makes x and y lim dynamic
    return hv_to_bokeh_obj( TOF_dmap.opts(width=width,height=height,ylim=ylim,xlim=xlim, xlabel=xlabel, ylabel=ylabel, title = title))

def smallData_table(pipe_or_buffer, width=500, height=400):
    TOF_dmap = hv.DynamicMap(hv.Table, streams=[pipe_or_buffer])
    return hv_to_bokeh_obj( TOF_dmap.opts(width=width,height=height))

def pnCCDData_plot(pipe_or_buffer, width=500, height=500,ylim=(-0.5,0.5),xlim=(-0.5,0.5), zlim=(None,None), title=None, logz = True):
    TOF_dmap = hv.DynamicMap(hv.Image, streams=[pipe_or_buffer]).redim.range(z = zlim)
    #TOF_dmap_opt = rasterize(TOF_dmap)
    TOF_dmap_opt = TOF_dmap
    #TOF_dmap_opt = datashade(TOF_dmap, streams=[PlotSize, RangeXY], dynamic=True)
    return TOF_dmap_opt.opts(width=width,height=height,ylim=ylim,xlim=xlim, logz = logz, title = title, colorbar = True, cmap = colormap_pnCCD)

def pnCCDData_plot__2(pipe_or_buffer, width=500, height=500,ylim=(-0.5,0.5),xlim=(-0.5,0.5), zlim=(None,None), title=None, logz = True):
    TOF_dmap = hv.HoloMap({(i): hv.DynamicMap(hv.Image, streams=[pipe_or_buffer]).redim.range(z = (None, i)) for i in [0.1,1,10,100]}, kdims='Z lower Bound')
    #TOF_dmap_opt = rasterize(TOF_dmap)
    TOF_dmap_opt = TOF_dmap
    #TOF_dmap_opt = datashade(TOF_dmap, streams=[PlotSize, RangeXY], dynamic=True)
    return TOF_dmap_opt.opts(width=width,height=height,ylim=ylim,xlim=xlim, logz = logz, title = title, colorbar = True, cmap = 'Plasma')

def pnCCDData_plot_d_dmap(pipe_or_buffer, width=500, height=500,ylim=(-0.5,0.5),xlim=(-0.5,0.5), zlim=(None,None), title=None, logz = True):
    TOF_dmap = hv.DynamicMap(hv.Image, streams=[pipe_or_buffer]).redim.range(z = zlim)
    #TOF_dmap_opt = rasterize(TOF_dmap)
    TOF_dmap_opt = TOF_dmap_opt.opts(width=width,height=height,ylim=ylim,xlim=xlim, logz = logz, title = title, colorbar = True, cmap = 'Plasma')
    #TOF_dmap_opt = datashade(TOF_dmap, streams=[PlotSize, RangeXY], dynamic=True)
    return hv_to_bokeh_obj( TOF_dmap_opt ), TOF_dmap_opt 

def start_stop_dataThread():
    #print("~~~~~~~~~~~~~~~~ ATTEMPT STOPPING THREAD")
    #~ thread.end()
    print("Attempt Clear PNCCD MEAN BUFFER")
    _SQSbuffer__pnCCD_mean_helper = online.DataBuffer(100)
    print(_SQSbuffer__pnCCD_mean_helper.length)

# Data buffers for live stream
buffer_length = 1500
mean_1_length = 10
mean_2_length = 20
_SQSbuffer__GMD_history = online.DataBuffer(buffer_length)
_SQSbuffer__pnCCD_integral = online.DataBuffer(buffer_length)
_SQSbuffer__pnCCD_mean_1_integral = online.DataBuffer(buffer_length)
_SQSbuffer__pnCCD_mean_2_integral = online.DataBuffer(buffer_length)
_SQSbuffer__pnCCD_integral_proc = online.DataBuffer(buffer_length)
_SQSbuffer__pnCCD_mean_1_integral_proc = online.DataBuffer(buffer_length)
_SQSbuffer__pnCCD_mean_1_integral_proc_top = online.DataBuffer(buffer_length)
_SQSbuffer__pnCCD_mean_1_integral_proc_bottom = online.DataBuffer(buffer_length)
_SQSbuffer__pnCCD_mean_1_integral_proc_right = online.DataBuffer(buffer_length)
_SQSbuffer__pnCCD_mean_1_integral_proc_left = online.DataBuffer(buffer_length)
_SQSbuffer__pnCCD_mean_2_integral_proc = online.DataBuffer(buffer_length)
_SQSbuffer__pnCCD_mean_helper_1 = online.DataBuffer(mean_1_length)
_SQSbuffer__pnCCD_mean_helper_2 = online.DataBuffer(mean_2_length)
_SQSbuffer__xgm_mean_helper_1 = online.DataBuffer(mean_1_length)
_SQSbuffer__xgm_mean_helper_2 = online.DataBuffer(mean_2_length)
_SQSbuffer__counter = online.DataBuffer(buffer_length)
_SQSbuffer__counter_time = online.DataBuffer(buffer_length)
print("...2")

# Data pipes and buffers for plots
## pipes provide a full update of data to the underlying object eg. plot
## buffers add only a single value to the plot and may kick one out when number of elements in the buffer has reached the length/size of the buffer
_pipe__pnCCD_single = Pipe(data=[])
_pipe__pnCCD_mean_1 = Pipe(data=[])
_pipe__pnCCD_mean_2 = Pipe(data=[])
_pipe__pnCCD_integral = Pipe(data=[])
_pipe__pnCCD_mean_1_integral = Pipe(data=[])
_pipe__pnCCD_mean_2_integral = Pipe(data=[])
_pipe__pnCCD_integral_by_gmd = Pipe(data=[])
_pipe__pnCCD_mean_1_integral_by_gmd = Pipe(data=[])
_pipe__pnCCD_mean_1_integral_by_gmd_top = Pipe(data=[])
_pipe__pnCCD_mean_1_integral_by_gmd_bottom = Pipe(data=[])
_pipe__pnCCD_mean_1_integral_by_gmd_right = Pipe(data=[])
_pipe__pnCCD_mean_1_integral_by_gmd_left = Pipe(data=[])
_pipe__pnCCD_mean_2_integral_by_gmd = Pipe(data=[])
_pipe__GMD_history = Pipe(data=[])
_pipe__pnCCD_hits__last_hit = Pipe(data=[])
_pipe__trainId__last_hit = Pipe(data=[])

# SETUP PLOTS
print("...3")
# example for coupled plots
#         layout = hv.Layout(largeData_line_plot(_pipe__TOF_single, title="TOF single shots - LIVE") + largeData_line_plot(_pipe__TOF_single, title="TOF single shots - LIVE 2", cmap=['red'])).cols(1)

## pnCCD

bokeh_live_pnCCD =  hv_to_bokeh_obj( pnCCDData_plot(_pipe__pnCCD_single, title="pnCCD single shots - LIVE", width = 600, height =500,zlim=(pnCCD_color_lower_z_lim,pnCCD_color_upper_z_lim), logz = True) )
bokeh_mean_1_pnCCD =  hv_to_bokeh_obj( pnCCDData_plot(_pipe__pnCCD_mean_1, title="pnCCD single shots - rolling AVG 1 - length "+str(mean_1_length), width = 600, height =500,zlim=(pnCCDavg_color_lower_z_lim,pnCCDavg_color_upper_z_lim), logz = True) )
bokeh_mean_2_pnCCD_hv = pnCCDData_plot(_pipe__pnCCD_mean_2, title="pnCCD single shots - rolling AVG 2 - length "+str(mean_2_length), width = 600, height =500,zlim=(pnCCDavg_color_lower_z_lim,pnCCDavg_color_upper_z_lim), logz = True)
bokeh_mean_2_pnCCD =  hv_to_bokeh_obj( bokeh_mean_2_pnCCD_hv )

bokeh_mean_1_pnCCD__duplicate = hv_to_bokeh_obj( pnCCDData_plot(_pipe__pnCCD_mean_1, title="pnCCD single shots - rolling AVG 1 - length "+str(mean_1_length), width = 900, height =750,zlim=(pnCCDavg_color_lower_z_lim,pnCCDavg_color_upper_z_lim), logz = True) )

bokeh_buffer_pnCCD_integral = smallData_line_plot(_pipe__pnCCD_integral, title="pnCCD single shots integral", xlim=(None,None), ylim=(None, None), width = 600, height = 250, xlabel='Time (now = 0) in s')
bokeh_buffer_pnCCD_mean_1_integral = smallData_line_plot(_pipe__pnCCD_mean_1_integral, title="pnCCD avg 1 integral", xlim=(None,None), ylim=(None, None), width = 600, height = 250, xlabel='Time (now = 0) in s')
bokeh_buffer_pnCCD_mean_2_integral = smallData_line_plot(_pipe__pnCCD_mean_2_integral, title="pnCCD avg 2 integral", xlim=(None,None), ylim=(None, None), width = 600, height = 250, xlabel='Time (now = 0) in s')

bokeh_buffer_pnCCD_integral_proc = smallData_line_plot(_pipe__pnCCD_integral_by_gmd, title="pnCCD single shots integral / XGM", xlim=(None,None), ylim=(None, None), width = 600, height = 250, xlabel='Time (now = 0) in s')
bokeh_buffer_pnCCD_mean_1_integral_proc = smallData_line_plot(_pipe__pnCCD_mean_1_integral_by_gmd, title="pnCCD avg 1 integral / XGM", xlim=(None,None), ylim=(None, None), width = 600, height = 250, xlabel='Time (now = 0) in s')
bokeh_buffer_pnCCD_mean_2_integral_proc = smallData_line_plot(_pipe__pnCCD_mean_2_integral_by_gmd, title="pnCCD avg 2 integral / XGM", xlim=(None,None), ylim=(None, None), width = 600, height = 250, xlabel='Time (now = 0) in s')

bokeh_buffer_pnCCD_mean_1_integral_proc_top = smallData_line_plot(_pipe__pnCCD_mean_1_integral_by_gmd_top, title="TOP -- pnCCD avg 1 integral / XGM", xlim=(None,None), ylim=(None, None), width = 600, height = 250, xlabel='Time (now = 0) in s')
bokeh_buffer_pnCCD_mean_1_integral_proc_bottom = smallData_line_plot(_pipe__pnCCD_mean_1_integral_by_gmd_bottom, title="BOTTOM -- pnCCD avg 1 integral / XGM", xlim=(None,None), ylim=(None, None), width = 600, height = 250, xlabel='Time (now = 0) in s')
bokeh_buffer_pnCCD_mean_1_integral_proc_right = smallData_line_plot(_pipe__pnCCD_mean_1_integral_by_gmd_right, title="RIGHT -- pnCCD avg 1 integral / XGM", xlim=(None,None), ylim=(None, None), width = 600, height = 250, xlabel='Time (now = 0) in s')
bokeh_buffer_pnCCD_mean_1_integral_proc_left = smallData_line_plot(_pipe__pnCCD_mean_1_integral_by_gmd_left, title="LEFT -- pnCCD avg 1 integral / XGM", xlim=(None,None), ylim=(None, None), width = 600, height = 250, xlabel='Time (now = 0) in s')


## GMD
bokeh_buffer_gmd = smallData_line_plot(_pipe__GMD_history, title="GMD History", xlim=(None,None), ylim=(None, None), width = 500, height =250)

## SET UP Additional Widgets
bokeh_last_hit_trainid_label = Div(text='<p><span style="font-size:20pt">#############<span></p>', width = 400, height = 50)
bokeh_pnccd_live_trainid_label = Div(text='<p><span style="font-size:20pt">#############<span></p>', width = 600, height = 50)
bokeh_daq_frequency_label = Div(text='<p><span style="font-size:20pt">Analysis Frequency: <span></p>', width = 600, height = 50)
bokeh_buffer_last_hit_trainids = Div(text='<p><span style="font-size:20pt">#############<br><br>#############<br><br>#############<br><br>#############<br><br>#############<br><br><span></p>', width = 200, height = 400)
bokeh_spacer_height_250 = Div(text=' ', width = 50, height = 250)
bokeh_spacer_width_600 = Div(text=' ', width = 600, height = 50)
print("...3")

## SET UP UI Interaction
def testButtonCallback():
    print("$$$$$$$$$$$$$$ TEST BUTTON CALLBACK")
    bokeh_mean_2_pnCCD_hv.redim.range(z = (10,None))
    pass
bokeh_button_test = Button(label = "Test", button_type="success")
bokeh_button_test.on_click(testButtonCallback)

# SET UP BOKEH LAYOUT
#
bokeh_row_0 = row(bokeh_pnccd_live_trainid_label , bokeh_daq_frequency_label)
bokeh_row_1 = row(bokeh_live_pnCCD,bokeh_mean_1_pnCCD,bokeh_mean_2_pnCCD)
bokeh_row_2 = row(bokeh_buffer_pnCCD_integral,bokeh_buffer_pnCCD_mean_1_integral,bokeh_buffer_pnCCD_mean_2_integral, bokeh_buffer_gmd)
bokeh_row_3 = row(bokeh_buffer_pnCCD_integral_proc,bokeh_spacer_width_600,bokeh_buffer_pnCCD_mean_2_integral_proc)#bokeh_button_test)
bokeh_row_4 = row(column(bokeh_spacer_height_250,bokeh_buffer_pnCCD_mean_1_integral_proc_left),column(bokeh_buffer_pnCCD_mean_1_integral_proc_top,bokeh_buffer_pnCCD_mean_1_integral_proc,bokeh_buffer_pnCCD_mean_1_integral_proc_bottom),column(bokeh_spacer_height_250,bokeh_buffer_pnCCD_mean_1_integral_proc_right), bokeh_mean_1_pnCCD__duplicate)

bokeh_layout = column(bokeh_row_0,bokeh_row_1, bokeh_row_2, bokeh_row_3,bokeh_row_4)
print("...4")
# add bokeh layout to current doc
doc.add_root(bokeh_layout)
print("...5")
# Start Thread for Handling of the Live Data Strem
#~ thread = Thread(target=makeBigData)
thread = makeBigDataThread()
thread.start()
