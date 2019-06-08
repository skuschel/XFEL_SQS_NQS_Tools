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

from holoviews.plotting.util import process_cmap
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
gmd_in_stream = False

two_monitors = False
large_monitor = True

colormap_pnCCD = 'Plasma'
colormap_pnCCD = process_cmap('rainbow',provider='colorcet')
colormap_pnCCD = process_cmap('jet',provider='matplotlib')

oa_disp_mod = 8 # display modulo set on oa freq - every xxxth shot display will be refreshed

img_downscale = 30

makeBigData_stop = False
# DATA CONFIG
#~ pnccd_crop_limits = [256,768,256,768]
pnccd_crop_limits = [0,1024,0,1024]
pnccd_dims = [pnccd_crop_limits[1]-pnccd_crop_limits[0],pnccd_crop_limits[3]-pnccd_crop_limits[2]]
N_datapts = 31000 # total number of TOF datapoints that are visualized
start_tof = 59000 # index of first TOF datapoint considered
single_photon_adu = 250
background_pnCCD = np.zeros(shape=(1024,1024))
background_max_pnCCD = np.zeros(shape=(1024,1024))
dark_pnCCD = np.zeros(shape=(1024,1024))
get_background_pnCCD = True
get_background_max_pnCCD = True
get_dark_pnCCD = False
pnCCD_integral_hit_threshold = 5e5# 1.5e5
pnCCD_integral_combines_hit_threshold = 2.5e5# 1.5e5
#~ tof_height_hit_threshold = 9e6# 1.5e5
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
    d['pnCCD'] = np.squeeze(d['pnCCD'])
    
    #~ print(str(np.min(d['pnCCD'])) + "   ----   "+str(np.mean(d['pnCCD']))+ "   ----   "+str(np.mean(d['pnCCD'])))
    
    
    if False:
        cm_mode_avgs_upper = np.mean(d['pnCCD'][0:150,:], axis = 0)
        cm_mode_cor_upper = np.matlib.repmat(cm_mode_avgs_upper,512,1)
        cm_mode_avgs_lower = np.mean(d['pnCCD'][(1023-150):1023,:], axis = 0)
        cm_mode_cor_lower = np.matlib.repmat(cm_mode_avgs_lower,512,1)

        cm_mode_cor = np.concatenate((cm_mode_cor_upper,cm_mode_cor_lower))
        d['pnCCD'] = d['pnCCD'] - cm_mode_cor
    if False:
        cm_mode_avgs_upper = np.mean(d['pnCCD'][:,0:200], axis = 1)
        cm_mode_cor_upper = np.transpose(np.matlib.repmat(cm_mode_avgs_upper,512,1))
        cm_mode_avgs_lower = np.mean(d['pnCCD'][:,(1023-200):1023], axis = 1)
        cm_mode_cor_lower = np.transpose(np.matlib.repmat(cm_mode_avgs_lower,512,1))

        cm_mode_cor = np.concatenate((cm_mode_cor_upper,cm_mode_cor_lower),axis =1)
        d['pnCCD'] = d['pnCCD'] - cm_mode_cor
    d['pnCCD_hit_find'] = d['pnCCD']
    if get_background_pnCCD:
        d['pnCCD'] = d['pnCCD'] - background_pnCCD
    if get_background_max_pnCCD:
        d['pnCCD_hit_find'] = d['pnCCD_hit_find'] - background_max_pnCCD
        d['pnCCD_hit_find'][d['pnCCD_hit_find']<0]=0
    if get_dark_pnCCD:
        d['pnCCD'] = d['pnCCD']- dark_pnCCD
    d['pnCCD_full'] = d['pnCCD']
    d['pnCCD_small'] = d['pnCCD'][256:768,256:768]
    d['pnCCD'] = d['pnCCD'][pnccd_crop_limits[0]:pnccd_crop_limits[1],pnccd_crop_limits[2]:pnccd_crop_limits[3]]
    #~ d['pnCCD'] = d['pnCCD'] / single_photon_adu # convert to number of photons
    #~ d['pnCCD_n_lit'] = np.sum(d['pnCCD'] >= 1) # get number of lit px
    #~ d['pnCCD_integral'] = np.sum(d['pnCCD'])
    return d

def makeDatastreamPipeline(source):
    ds = online.servedata(source) #get the datastream
    ds = online.getTof(ds,idx_range=[start_tof,end_tof],baselineTo=1000) #get the tofs
    ds = processTofs(ds) #treat the tofs
    ds = online.getSomeDetector(ds, name='tid', spec0='SQS_DIGITIZER_UTC1/ADC/1:network', spec1='digitizers.trainId') #get current trainids from digitizer property
    #ds = online.getSomeDetector(ds, name='tid', spec0='SA3_XTD10_XGM/XGM/DOOCS:output', spec1='timestamp.tid', readFromMeta=True) #get current trainids from gmd property
    if pnCCD_in_stream:
        ds = online.getSomePnCCD(ds, name='pnCCD', spec0='SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output', spec1='data.image') #get pnCCD
        #~ ds = online.getSomeDetector(ds, name='tid', spec0='SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output', spec1='timestamp.tid', readFromMeta=True) #get current trainids from gmd property
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
    #~ global background_pnCCD
    #~ background_pnCCD = background_pnCCD[256:768,256:768]
    perf = online_bokeh.performanceMonitor() # outputs to console info on performance - eg what fraction of data was not pulled from live stream and thus missed
    #print
    n=-1
    hit_found = False
    print("Start Live Display")
    for data in ds:
        n+=1
        perf.iteration()
        if data['pnCCD_in_data']: ## skip analysis if now pn ccd in data
            # performance monitor - frequency of displaying data + loop duration
            

            # Hand Data from datastream to plots and performance monitor

            # Thinga for data buffers
            ## TOF integral
            if tof_in_stream:
                integral_tof = abs(np.sum(data['tof']))
                height_tof = abs(np.min(data['tof']))
                _SQSbuffer__TOF_integral(integral_tof)
                _SQSbuffer__TOF_height(height_tof)
            if gmd_in_stream:
                _SQSbuffer__GMD_history(data['gmd'][0])
            if pnCCD_in_stream:
                pnCCD_single_full_bg_cor = np.squeeze(data['pnCCD'])
                pnCCD_single_full = pnCCD_single_full_bg_cor.copy()
                pnCCD_single_full[pnCCD_single_full<1] = 1
                #~ pnCCD_integral = data['pnCCD_integral'] 
                #~ _SQSbuffer__pnCCD_mean_helper(pnCCD_single_full_bg_cor)
                #~ _SQSbuffer__pnCCD_mean_helper_2(pnCCD_single_full_bg_cor)
                 
                #~ pnCCD_max = np.max(pnCCD_single_full_bg_cor) 
                #~ pnCCD_litpx = d['pnCCD_n_lit']
                #~ pnCCD_litpx = np.sum(pnCCD_single_full_bg_cor >= single_photon_adu)
                
                pnCCD_single = pnCCD_single_full
                #~ pnCCD_single = np.mean(_SQSbuffer__pnCCD_mean_helper,axis=0)
                #~ pnCCD_single_mean_2 = np.mean(_SQSbuffer__pnCCD_mean_helper_2,axis=0)
                #~ print(np.min(pnCCD_single_mean_2))
                #~ print(np.mean(pnCCD_single_mean_2))
                
                #~ pnCCD_integral = np.sum(pnCCD_single) 
                pnCCD_integral = np.sum(data['pnCCD_small'])
                pnCCD_integral_hit_find = np.sum(data['pnCCD_hit_find'])
                _SQSbuffer__pnCCD_integral(pnCCD_integral_hit_find)
                if height_tof>500 or integral_tof>1e6:
                    hit_found = True
                    last_hit_pnCCD = pnCCD_single_full
                    last_hit_TOF = data['tof']
                    _SQSbuffer__TOF_hits__last_hit(np.squeeze(last_hit_TOF))
                    _SQSbuffer__pnCCD_hits__last_hit(np.squeeze(data['pnCCD_full']))
                    _SQSbuffer__trainId__last_hit(data['tid'])
                    _SQSbuffer__pnCCD_hitrate_helper(1)
                else:
                    _SQSbuffer__pnCCD_hitrate_helper(0)
                _SQSbuffer__pnCCD_hitrate(np.mean(_SQSbuffer__pnCCD_hitrate_helper)*100)
                if not get_background_max_pnCCD:
                    pnCCD_hitfinder_val = pnCCD_integral
                else:
                    pnCCD_hitfinder_val = pnCCD_integral_hit_find
                if pnCCD_hitfinder_val > pnCCD_integral_hit_threshold or ( pnCCD_hitfinder_val > pnCCD_integral_combines_hit_threshold and height_tof>400 ):#2.623e5:
                    hit_img_full = np.squeeze(np.asarray(pnCCD_single_full))
                    hit_img_full[hit_img_full<0]=0
                    #~ print(hit_img_full.shape)
                    resized_hit_img = imresize(hit_img_full.astype(np.uint16),img_downscale)
                    _SQSbuffer__pnCCD_hits(resized_hit_img)
                    _SQSbuffer__pnCCD_hitrate_helper_2(1)
                    _SQSbuffer__pnCCD_hits_tids(data['tid'])
                    _SQSbuffer__pnCCD_hits__pnccdDetect__last_hit(np.squeeze(np.asarray(data['pnCCD_full'])))
                    _SQSbuffer__TOF_hits__pnccdDetect__last_hit(np.squeeze(data['tof']))
                    _SQSbuffer__trainId__pnccdDetect__last_hit(data['tid'])
                else:
                    _SQSbuffer__pnCCD_hitrate_helper_2(0)
                _SQSbuffer__pnCCD_hitrate_2(np.mean(_SQSbuffer__pnCCD_hitrate_helper_2)*100)
            _SQSbuffer__counter(n)
            ## TrainId
            trainId = str(data['tid'])
            # Things for add next tick callback
            if n%oa_disp_mod==0: # skip plotting 
                callback_data_dict = dict()
                callback_data_dict['OA_frequency_label'] = str(round(perf.freq_avg,1))
                callback_data_dict['OA_disp_frequency_label'] = str(round(perf.freq_avg / oa_disp_mod,1))
                callback_data_dict['OA_avg_hitrate_label'] = [str(round(np.mean(_SQSbuffer__pnCCD_hitrate.data),2)),str(round(np.mean(_SQSbuffer__pnCCD_hitrate_2.data),2))]
                if tof_in_stream:
                    callback_data_dict["tof_trace"] = ( np.squeeze(data['x_tof']) , np.squeeze(data['tof']))
                    callback_data_dict["tof_integral"] = ( _SQSbuffer__counter.data , _SQSbuffer__TOF_integral.data )
                    callback_data_dict["tof_height"] = ( _SQSbuffer__counter.data , _SQSbuffer__TOF_height.data )
                if pnCCD_in_stream:
                    callback_data_dict["pnCCD_single"] = (pnCCD_single)
                    #~ callback_data_dict["pnCCD_single"] = (np.squeeze(data['pnCCD_hit_find']))
                    callback_data_dict["pnCCD_single_tid"] = (trainId)
                    callback_data_dict["pnCCD_integral"] = (_SQSbuffer__counter.data , _SQSbuffer__pnCCD_integral.data)
                    callback_data_dict["pnCCD_recent_hits"] = (_SQSbuffer__pnCCD_hits.data)
                    callback_data_dict["pnCCD_recent_hits_tids"] = (_SQSbuffer__pnCCD_hits_tids.data)
                    callback_data_dict["pnCCD_hitrate"] = (_SQSbuffer__counter.data , _SQSbuffer__pnCCD_hitrate.data)
                    callback_data_dict["pnCCD_hitrate_2"] = (_SQSbuffer__counter.data , _SQSbuffer__pnCCD_hitrate_2.data)
                    if hit_found:
                        callback_data_dict["pnCCD_last_hit"] = last_hit_pnCCD
                        callback_data_dict["TOF_last_hit"] = ( np.squeeze(data['x_tof']) , np.squeeze(last_hit_TOF))
                        callback_data_dict["pnCCD_last_hit_tid"] = str(round((_SQSbuffer__trainId__last_hit.data[0])))
                        #~ bokeh_last_hit_trainid_label.text = trainId
                    #~ else:
                        #~ callback_data_dict["pnCCD_last_hit"] = pnCCD_single_mean_2#last_hit_pnCCD
                if gmd_in_stream:
                    #~ callback_data_dict["pnCCD_last_hit_tid"] = 'XGM : '+str(round(data['gmd'][0],2))+" uJ"
                    callback_data_dict["gmd_history"] = ( _SQSbuffer__counter.data , _SQSbuffer__GMD_history.data )

                buffer_or_pipe_dict = dict()
                buffer_or_pipe_dict['OA_frequency_label'] = None
                buffer_or_pipe_dict['OA_disp_frequency_label'] = None
                buffer_or_pipe_dict['OA_avg_hitrate_label'] = None
                if tof_in_stream:
                    buffer_or_pipe_dict["tof_trace"] = _pipe__TOF_single
                    buffer_or_pipe_dict["tof_integral"] = _pipe__TOF_integral
                    buffer_or_pipe_dict["tof_height"] = _pipe__TOF_height
                if pnCCD_in_stream:
                    buffer_or_pipe_dict["pnCCD_single"] = _pipe__pnCCD_single
                    buffer_or_pipe_dict["pnCCD_single_tid"] = None
                    buffer_or_pipe_dict["pnCCD_integral"] = _pipe__pnCCD_integral
                    buffer_or_pipe_dict["pnCCD_recent_hits"] = _pipe__pnCCD_hits_list
                    buffer_or_pipe_dict["pnCCD_recent_hits_tids"] = _pipe__pnCCD_hits_tids
                    buffer_or_pipe_dict["pnCCD_hitrate"] = _pipe__pnCCD_hitrate
                    buffer_or_pipe_dict["pnCCD_hitrate_2"] = _pipe__pnCCD_hitrate_2
                    if hit_found:
                        hit_found = False
                        buffer_or_pipe_dict["pnCCD_last_hit"] = _pipe__pnCCD_hits__last_hit
                        buffer_or_pipe_dict["pnCCD_last_hit_tid"] = None
                        buffer_or_pipe_dict["TOF_last_hit"] = _pipe__TOF_hits__last_hit
                    #~ else:
                        #~ buffer_or_pipe_dict["pnCCD_last_hit"] = _pipe__pnCCD_hits__last_hit
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
        if key is "pnCCD_recent_hits":
            fill_recent_hits_pipes(buffer_or_pipe_dict[key],callback_data_dict[key], n)
        elif key is 'pnCCD_single_tid':
            bokeh_pnccd_live_trainid_label.text = '<p><span style="font-size:20pt">Train ID: '+callback_data_dict[key]+'<span></p>'
            pass
        elif key is 'pnCCD_last_hit_tid':
            bokeh_last_hit_trainid_label.text = '<p><span style="font-size:20pt">Train ID: '+callback_data_dict[key]+'<span></p>'
            #~ hv_dmap_last_hit_pnCCD.title = callback_data_dict[key]
        elif key is 'OA_frequency_label':
            bokeh_daq_frequency_label.text = '<p><span style="font-size:20pt">Analysis Frequency: '+callback_data_dict[key]+' Hz<span></p>'
        elif key is 'OA_disp_frequency_label':
            bokeh_daq_disp_frequency_label.text = '<p><span style="font-size:20pt">Display Frequency: '+callback_data_dict[key]+' Hz<span></p>'
        elif key is 'OA_avg_hitrate_label':
            bokeh_oa_avg_hitrate_label.text = '<p><span style="font-size:20pt">AVG Hitrate: tof '+callback_data_dict[key][0]+' % | pnccd '+callback_data_dict[key][1]+' %<span></p>'
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
    #print("#####  "+str(n)+"  ######## Called fill recent hits pipes @ n = "+ str(n))
    #print(data.shape)
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
    return hv_to_bokeh_obj( TOF_dmap_opt.opts(width=width,height=height,ylim=ylim,xlim=xlim, logz = logz, title = title, colorbar = True, cmap = colormap_pnCCD) )

def pnCCDData_plot_d_dmap(pipe_or_buffer, width=500, height=500,ylim=(-0.5,0.5),xlim=(-0.5,0.5), zlim=(None,None), title=None, logz = True):
    TOF_dmap = hv.DynamicMap(hv.Image, streams=[pipe_or_buffer]).redim.range(z = zlim)
    #TOF_dmap_opt = rasterize(TOF_dmap)
    TOF_dmap_opt = TOF_dmap_opt.opts(width=width,height=height,ylim=ylim,xlim=xlim, logz = logz, title = title, colorbar = True, cmap = 'Plasma')
    #TOF_dmap_opt = datashade(TOF_dmap, streams=[PlotSize, RangeXY], dynamic=True)
    return hv_to_bokeh_obj( TOF_dmap_opt ), TOF_dmap_opt 



# Data buffers for live stream
buffer_length = 300
_SQSbuffer__TOF_integral = online.DataBuffer(buffer_length)
_SQSbuffer__TOF_height = online.DataBuffer(buffer_length)
_SQSbuffer__GMD_history = online.DataBuffer(buffer_length)
_SQSbuffer__pnCCD_integral = online.DataBuffer(buffer_length)
_SQSbuffer__pnCCD_hits = online.DataBuffer(5)
_SQSbuffer__pnCCD_mean_helper = online.DataBuffer(100)
_SQSbuffer__pnCCD_mean_helper_2 = online.DataBuffer(20)
_SQSbuffer__pnCCD_hits_tids = online.DataBuffer(5)
_SQSbuffer__pnCCD_hitrate_helper = online.DataBuffer(300)
_SQSbuffer__pnCCD_hitrate = online.DataBuffer(buffer_length)
_SQSbuffer__pnCCD_hitrate_helper_2 = online.DataBuffer(300)
_SQSbuffer__pnCCD_hitrate_2 = online.DataBuffer(buffer_length)
_SQSbuffer__pnCCD_hits__last_hit = online.DataBuffer(1)
_SQSbuffer__TOF_hits__last_hit = online.DataBuffer(1)
_SQSbuffer__trainId__last_hit = online.DataBuffer(1)
_SQSbuffer__pnCCD_hits__pnccdDetect__last_hit = online.DataBuffer(5)
_SQSbuffer__TOF_hits__pnccdDetect__last_hit = online.DataBuffer(5)
_SQSbuffer__trainId__pnccdDetect__last_hit = online.DataBuffer(5)
for k in range(5):
    _SQSbuffer__pnCCD_hits(imresize(np.zeros(shape=(pnccd_dims[0],pnccd_dims[1])),img_downscale))
    _SQSbuffer__pnCCD_hits_tids((0))
_SQSbuffer__counter = online.DataBuffer(buffer_length)
print("...2")

# Data pipes and buffers for plots
## pipes provide a full update of data to the underlying object eg. plot
## buffers add only a single value to the plot and may kick one out when number of elements in the buffer has reached the length/size of the buffer
_pipe__TOF_single = Pipe(data=[])
#_buffer__TOF_integral = Buffer(pd.DataFrame({'x':[],'y':[]}, columns=['x','y']), length=100, index=False)
_pipe__TOF_integral = Pipe(data=[])
_pipe__TOF_height = Pipe(data=[])
_pipe__pnCCD_single = Pipe(data=[])
_pipe__pnCCD_integral = Pipe(data=[])
_pipe__GMD_history = Pipe(data=[])
_pipe__pnCCD_hitrate = Pipe(data=[])
_pipe__pnCCD_hitrate_2 = Pipe(data=[])
_pipe__pnCCD_hits_tids = Pipe(data=[])
_pipe__pnCCD_hits_list = list()
for i in range(5):
    _pipe__pnCCD_hits_list.append(Pipe(data=[]))
_pipe__pnCCD_hits__last_hit = Pipe(data=[])
_pipe__TOF_hits__last_hit = Pipe(data=[])
_pipe__trainId__last_hit = Pipe(data=[])

# SETUP PLOTS
print("...3")
# example for coupled plots
#         layout = hv.Layout(largeData_line_plot(_pipe__TOF_single, title="TOF single shots - LIVE") + largeData_line_plot(_pipe__TOF_single, title="TOF single shots - LIVE 2", cmap=['red'])).cols(1)
## TOF
if two_monitors:
    bokeh_live_tof =  largeData_line_plot(_pipe__TOF_single, title="TOF single shots - LIVE", width = 1000, height=500)
    bokeh_buffer_tof_integral = smallData_line_plot(_pipe__TOF_integral, title="TOF trace full range integral (absolute)", xlim=(None,None), ylim=(0, None), width = 400, height = 250)
    bokeh_buffer_tof_height = smallData_line_plot(_pipe__TOF_height, title="TOF trace height (absolute)", xlim=(None,None), ylim=(0, None), width = 400, height = 250)
else:
    bokeh_live_tof =  largeData_line_plot(_pipe__TOF_single, title="TOF single shots - LIVE", width = 500, height=500)
    bokeh_buffer_tof_integral = smallData_line_plot(_pipe__TOF_integral, title="TOF trace full range integral (absolute)", xlim=(None,None), ylim=(0, None), width = 400, height = 250)
    bokeh_buffer_tof_height = smallData_line_plot(_pipe__TOF_height, title="TOF trace height (absolute)", xlim=(None,None), ylim=(0, None), width = 400, height = 250)

## pnCCD
bokeh_live_pnCCD =  pnCCDData_plot(_pipe__pnCCD_single, title="pnCCD single shots - LIVE", width = 600, height =500,zlim=(0.1,None), logz = True)
bokeh_buffer_pnCCD_integral = smallData_line_plot(_pipe__pnCCD_integral, title="pnCCD single shots integral", xlim=(None,None), ylim=(None, None), width = 500, height = 250)
bokeh_hits_pnCCD_list = list()
if not large_monitor:
    for i in range(len(_pipe__pnCCD_hits_list)):
        bokeh_hits_pnCCD_list.append(pnCCDData_plot(_pipe__pnCCD_hits_list[i], title="pnCCD Most Recent Hits "+str(i), width=370, height=300,zlim=(0.1,None)))
else:
    for i in range(len(_pipe__pnCCD_hits_list)):
        bokeh_hits_pnCCD_list.append(pnCCDData_plot(_pipe__pnCCD_hits_list[i], title="pnCCD Most Recent Hits "+str(i), width=518, height=420,zlim=(0.1,None)))  

#~ last_hit_pnCCD_dmap = hv.DynamicMap(hv.Image, streams=[_pipe__pnCCD_hits__last_hit])
#~ last_hit_pnCCD_dmap_opt = last_hit_pnCCD_dmap.opts(title="pnCCD single shots - last hit high res", width = 600, height =500,zlim=(0.1,None), logz = True, colorbar = True, cmap = 'Plasma')
#~ bokeh_last_hit_pnCCD = hv_to_bokeh_obj( last_hit_pnCCD_dmap_opt )

bokeh_last_hit_pnCCD =  pnCCDData_plot(_pipe__pnCCD_hits__last_hit, title="pnCCD single shots - last hit high res", width = 600, height =500,zlim=(0.1,None))
bokeh_last_hit_tof =  largeData_line_plot(_pipe__TOF_hits__last_hit, title="TOF single shot - Last Hit", width = 500, height=250, ylim=(-4000,40))
bokeh_buffer_last_hit_trainid = smallData_scatter_plot(_pipe__trainId__last_hit, title="last hit trainid", xlim=(None,None), ylim=(None, None), width = 300, height = 200)
#~ bokeh_buffer_last_hit_trainids = smallData_table(_pipe__pnCCD_hits_tids, width=500, height=400)

print("...3")

## GMD
bokeh_buffer_pnccd_hitrate = smallData_2line_plot(_pipe__pnCCD_hitrate,_pipe__pnCCD_hitrate_2, title="Hitrate in % over window of 200 shots (~40s)", xlim=(None,None), ylim=(0, None), width = 500, height =250)

## Buttons
def button_tof_saver():
    print('$$$$$$$$$$$  SAVE TOF Detected Hit to File -- START')
    pnccd_d = _SQSbuffer__pnCCD_hits__last_hit.data
    tof_d = _SQSbuffer__TOF_hits__last_hit.data
    tid_d = _SQSbuffer__trainId__last_hit.data[0]
    fdir = 'output/'
    fname_pnccd = 'tof_detected_'+str(tid_d)+'_pnCCD.npy'
    fname_tof = 'tof_detected_'+str(tid_d)+'_tof.npy'
    np.save(fdir+fname_pnccd,pnccd_d)
    np.save(fdir+fname_tof,tof_d)
    print('$$$$$$$$$$$  SAVE TOF Detected Hit to File -- DONE')
    
#~ _SQSbuffer__pnCCD_hits__pnccdDetect__last_hit = online.DataBuffer(5)
#~ _SQSbuffer__TOF_hits__pnccdDetect__last_hit = online.DataBuffer(5)
#~ _SQSbuffer__trainId__pnccdDetect__last_hit = online.DataBuffer(5)
def button_pnccd_saver():
    print('$$$$$$$$$$$  SAVE pnCCD Detected Hit to File -- START')
    pnccd_d = _SQSbuffer__pnCCD_hits__pnccdDetect__last_hit.data
    tof_d = _SQSbuffer__TOF_hits__pnccdDetect__last_hit.data
    tid_d = _SQSbuffer__trainId__pnccdDetect__last_hit.data
    tid_str = ''
    for tid in tid_d:
        tid_str = tid_str + str(tid) + '_'
    fdir = 'output/'
    fname_pnccd = 'pnCCD_detected_'+tid_str+'_pnCCD.npy'
    fname_tof = 'pnCCD_detected_'+tid_str+'_tof.npy'
    np.save(fdir+fname_pnccd,pnccd_d)
    np.save(fdir+fname_tof,tof_d)
    print('$$$$$$$$$$$  SAVE pnCCD Detected Hit to File -- DONE')
    
bokeh_button_save_tof_hit = Button(label = "Emergency Save TOF detected Hit", button_type="success")
bokeh_button_save_tof_hit.on_click(button_tof_saver)
bokeh_button_save_pnccd_hit = Button(label = "Emergency Save pnCCD detected Hits", button_type="success")
bokeh_button_save_pnccd_hit.on_click(button_pnccd_saver)

## SET UP Additional Widgets
bokeh_last_hit_trainid_label = Div(text='<p><span style="font-size:20pt">#############<span></p>', width = 350, height = 50)
bokeh_pnccd_live_trainid_label = Div(text='<p><span style="font-size:20pt">#############<span></p>', width = 400, height = 50)
bokeh_daq_frequency_label = Div(text='<p><span style="font-size:20pt">Analysis Frequency: <span></p>', width = 400, height = 50)
bokeh_daq_disp_frequency_label = Div(text='<p><span style="font-size:20pt">Display Frequency: <span></p>', width = 400, height = 50)
bokeh_oa_avg_hitrate_label = Div(text='<p><span style="font-size:20pt">AVG Hitrate: <span></p>', width = 600, height = 50)
bokeh_spacer_1700_label = Div(text='<p><span style="font-size:20pt"> <span></p>', width = 1700, height = 50)

bokeh_buffer_last_hit_trainids = Div(text='<p><span style="font-size:20pt">#############<br>#############<br>#############<br>#############<br>#############<br><span></p>', width = 200, height = 200)
print("...3")

# SET UP BOKEH LAYOUT
#
## NORMAL MONITOR
#~ bokeh_row_1 = row(column(bokeh_pnccd_live_trainid_label,bokeh_live_pnCCD),bokeh_live_tof,column(bokeh_buffer_tof_integral,bokeh_buffer_tof_height),column(bokeh_buffer_pnCCD_integral,bokeh_buffer_pnccd_hitrate), column(row(bokeh_last_hit_trainid_label),bokeh_last_hit_pnCCD))
#~ bokeh_row_2 = row(bokeh_hits_pnCCD_list[1],bokeh_hits_pnCCD_list[2],bokeh_hits_pnCCD_list[3],bokeh_hits_pnCCD_list[4],bokeh_hits_pnCCD_list[0], column(bokeh_button_save_pnccd_hit,bokeh_buffer_last_hit_trainids), column(bokeh_button_save_tof_hit,bokeh_last_hit_tof))

#~ bokeh_row_interact  = row(bokeh_daq_frequency_label,bokeh_daq_disp_frequency_label, bokeh_oa_avg_hitrate_label)
#~ bokeh_layout = column(bokeh_row_1,bokeh_row_2, bokeh_row_interact)
## LARGE MONITOR
bokeh_row_1 = row(column(bokeh_pnccd_live_trainid_label,bokeh_live_pnCCD),bokeh_live_tof,column(bokeh_buffer_tof_integral,bokeh_buffer_tof_height),column(bokeh_buffer_pnCCD_integral,bokeh_buffer_pnccd_hitrate), column(row(bokeh_last_hit_trainid_label),bokeh_last_hit_pnCCD))
bokeh_row_2 = row(bokeh_spacer_1700_label,column(bokeh_button_save_pnccd_hit,bokeh_buffer_last_hit_trainids), column(bokeh_button_save_tof_hit,bokeh_last_hit_tof))
bokeh_row_3 = row(bokeh_hits_pnCCD_list[1],bokeh_hits_pnCCD_list[2],bokeh_hits_pnCCD_list[3],bokeh_hits_pnCCD_list[4],bokeh_hits_pnCCD_list[0])
bokeh_row_interact  = row(bokeh_daq_frequency_label,bokeh_daq_disp_frequency_label, bokeh_oa_avg_hitrate_label)
bokeh_layout = column(bokeh_row_1,bokeh_row_2,bokeh_row_3, bokeh_row_interact)
print("...4")
# add bokeh layout to current doc
doc.add_root(bokeh_layout)
print("...5")
# Start Thread for Handling of the Live Data Strem
#~ thread = Thread(target=makeBigData)
thread = makeBigDataThread()
thread.start()
