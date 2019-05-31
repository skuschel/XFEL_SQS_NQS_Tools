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
tof_in_stream = True
pnCCD_in_stream = True
gmd_in_stream = True

img_downscale = 15

makeBigData_stop = False
# DATA CONFIG
N_datapts = 35000 # total number of TOF datapoints that are visualized
start_tof = 485000 # index of first TOF datapoint considered
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
    d['tof'] = d['tof'][start_tof:end_tof] # cut out index range that we are interested in
    d['x_tof'] = x_tof # add values for x axis
    return d

class performanceMonitor():
    def __init__(self,trainStep=1):
        import time
        self.t_start = time.time()
        self.t_start_loop = self.t_start
        self.for_loop_step_dur = 0
        self.n=-1
        self.freq_avg = 0
        self.dt_avg = 0
        self.trainId = 0
        self.trainId_old = -1
        self.skip_count = 0
        self.trainStep = trainStep
        
    def iteration(self):
        self.n+=1
        self.dt = (time.time()-self.t_start)
        self.t_start = time.time()
        freq = 1/self.dt
        if self.n>0:
            self.dt_avg = (self.dt_avg * (self.n-1) + self.dt) / self.n
            freq_avg = 1/self.dt_avg
            loop_classification_percent = self.for_loop_step_dur/0.1*100
            if loop_classification_percent < 100:
                loop_classification_msg="OK"
            else:
                loop_classification_msg="TOO LONG!!!"
            print("Frequency: "+str(round(freq_avg,1)) +" Hz  |  skipped: "+str(self.skip_count)+" ( "+str(round(self.skip_count/self.n*100,1))+" %)  |  n: "+str(self.n)+"/"+str(self.trainId)+"  |  Loop benchmark: "+str(round(loop_classification_percent,1))+ " % (OK if <100%) - "+loop_classification_msg) 
        self.t_start_loop = time.time()
        
    def update_trainId(self,tid):
        self.trainId_old = self.trainId
        self.trainId = tid
        if self.n == 0:
            self.trainId_old = str(int(tid) -1)
        if int(self.trainId) - int(self.trainId_old) is not self.trainStep:
            self.skip_count +=1
            
    def time_for_loop_step(self):
        self.for_loop_step_dur = time.time()-self.t_start_loop

def makeDatastreamPipeline(source):
    ds = online.servedata(source) #get the datastream
    ds = online.getTof(ds) #get the tofs
    ds = processTofs(ds) #treat the tofs
    ds = online.getSomeDetector(ds, name='tid', spec0='SQS_DIGITIZER_UTC1/ADC/1:network', spec1='digitizers.trainId') #get current trainids from digitizer property
    #ds = online.getSomeDetector(ds, name='tid', spec0='SA3_XTD10_XGM/XGM/DOOCS:output', spec1='timestamp.tid', readFromMeta=True) #get current trainids from gmd property
    #if pnCCD_in_stream:
        #ds = online.getSomePnCCD(ds, name='pnCCD', spec0='SQS_NQS_PNCCD1MP/CAL/CORR_CM:output', spec1='data.image') #get pnCCD
        #ds = online.getSomeDetector(ds, name='tid', spec0='SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output', spec1='timestamp.tid', readFromMeta=True) #get current trainids from gmd property

    ds = online.getSomeDetector(ds, name='gmd', spec0='SA3_XTD10_XGM/XGM/DOOCS:output', spec1='data.intensitySa3TD') #get GMD
    return ds

def makeBigData():
    print("Source: "+ source) # print source set for data
    
    # Setup Data Stream Pipeline
    ds = makeDatastreamPipeline(source)
    
    perf = performanceMonitor() # outputs to console info on performance - eg what fraction of data was not pulled from live stream and thus missed
    #print
    n=-1
    print("Start Live Display")
    for data in ds:
        n+=1
        if n%1==0:
            # performance monitor - frequency of displaying data + loop duration
            perf.iteration()

            # Hand Data from datastream to plots and performance monitor
            
            # Thinga for data buffers
            ## TOF integral
            if tof_in_stream:
                integral_tof = abs(np.sum(data['tof']))
                _SQSbuffer__TOF_integral(integral_tof)
                _SQSbuffer__TOF_avg(data['tof'])
                if integral_tof > 2e5:
                    _SQSbuffer__TOF_hits(1)
                else:
                    _SQSbuffer__TOF_hits(0)
            if gmd_in_stream:
                _SQSbuffer__GMD_history(data['gmd'][0])
            #if pnCCD_in_stream:
             #   tmp_pnCCD = np.frombuffer(data['pnCCD'], dtype=np.float64)
              #  #print("Bytes per int in pnCCD array : "+str(tmp_pnCCD.shape[0] / 1024**2))
               # pnCCD_single = np.reshape(tmp_pnCCD, (1024,1024))
                #pnCCD_integral = np.sum(pnCCD_single)
                #_SQSbuffer__pnCCD_integral(pnCCD_integral)
                #if pnCCD_integral > 5e7:
                 #   _SQSbuffer__pnCCD_hits(imresize(pnCCD_single,img_downscale))
            _SQSbuffer__counter(n)
            # Things for add next tick callback
            if n%10 is not 0:
                callback_data_dict = dict()
                callback_data_dict["tof_trace"] = ( np.squeeze(data['x_tof']) , np.squeeze(data['tof']))
                callback_data_dict["tof_integral"] = ( _SQSbuffer__counter.data , _SQSbuffer__TOF_integral.data )
                callback_data_dict["tof_avg"] = ( np.squeeze(data['x_tof']) , np.squeeze(np.mean(_SQSbuffer__TOF_avg.data, axis=0)) )
                #callback_data_dict["pnCCD_single"] = (pnCCD_single)
                #callback_data_dict["pnCCD_integral"] = (_SQSbuffer__counter.data , _SQSbuffer__pnCCD_integral.data)
                #callback_data_dict["pnCCD_recent_hits"] = (_SQSbuffer__pnCCD_hits.data)
                callback_data_dict["gmd_history"] = ( _SQSbuffer__counter.data , _SQSbuffer__GMD_history.data )
                
                buffer_or_pipe_dict = dict()
                buffer_or_pipe_dict["tof_trace"] = _pipe__TOF_single
                buffer_or_pipe_dict["tof_integral"] = _pipe__TOF_integral
                #buffer_or_pipe_dict["tof_avg"] = _pipe__TOF_avg
                #buffer_or_pipe_dict["pnCCD_single"] = _pipe__pnCCD_single
                #buffer_or_pipe_dict["pnCCD_integral"] = _pipe__pnCCD_integral
                #buffer_or_pipe_dict["pnCCD_recent_hits"] = _pipe__pnCCD_hits_list
                #buffer_or_pipe_dict["gmd_history"] = _pipe__GMD_history
                
                if 'all_updates_next_tick_callback' in locals():
                    if all_updates_next_tick_callback in doc.session_callbacks:
                        doc.remove_next_tick_callback(all_updates_next_tick_callback)
                all_updates_next_tick_callback = callback_data_dict_into_callback(buffer_or_pipe_dict, callback_data_dict, n )
                ## TOF trace
                #x = np.squeeze(data['x_tof']); y = np.squeeze(data['tof'])
                #if 'tof_trace_next_tick_callback' in locals():
                #    if tof_trace_next_tick_callback in doc.session_callbacks:
                #        doc.remove_next_tick_callback(tof_trace_next_tick_callback)
                #tof_trace_next_tick_callback = data_into_buffer_or_pipe( _pipe__TOF_single,  ( x , y ), n )
                ### TOF integral
                #if 'tof_integral_next_tick_callback' in locals():
                #    if tof_integral_next_tick_callback in doc.session_callbacks:
                #        doc.remove_next_tick_callback(tof_integral_next_tick_callback)
                #tof_integral_next_tick_callback = data_into_buffer_or_pipe(_pipe__TOF_integral,  ( _SQSbuffer__counter.data , _SQSbuffer__TOF_integral.data ), n )
                #
                ### pnCCD Single
                #if 'pnCCD_live_single_next_tick_callback' in locals():
                #    if pnCCD_live_single_next_tick_callback in doc.session_callbacks:
                #        doc.remove_next_tick_callback(pnCCD_live_single_next_tick_callback)
                #pnCCD_live_single_next_tick_callback = data_into_buffer_or_pipe( _pipe__pnCCD_single,  (pnCCD_single), n )
                #if 'pnCCD_integral_next_tick_callback' in locals():
                #    if pnCCD_integral_next_tick_callback in doc.session_callbacks:
                #        doc.remove_next_tick_callback(pnCCD_integral_next_tick_callback)
                #pnCCD_integral_next_tick_callback = data_into_buffer_or_pipe( _pipe__pnCCD_single,  (_SQSbuffer__counter.data , _SQSbuffer__pnCCD_integral.data), n )
                #if 'pnCCD_recent_hits_next_tick_callback' in locals():
                #    if pnCCD_recent_hits_next_tick_callback in doc.session_callbacks:
                #        doc.remove_next_tick_callback(pnCCD_recent_hits_next_tick_callback)
                #pnCCD_recent_hits_next_tick_callback = data_into_recent_hits_pipes( _pipe__pnCCD_hits_list,  (_SQSbuffer__pnCCD_hits.data), n )
                #
                #_pipe__pnCCD_integral
                ### GMD history
                #if 'gmd_history_next_tick_callback' in locals():
                #    if gmd_history_next_tick_callback in doc.session_callbacks:
                #        doc.remove_next_tick_callback(gmd_history_next_tick_callback)
                #gmd_history_next_tick_callback = data_into_buffer_or_pipe(_pipe__GMD_history,  ( _SQSbuffer__counter.data , _SQSbuffer__GMD_history.data ), n )
                    
            # Things for performance analysis
            ## TrainId
            trainId = str(data['tid'])
            
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
    # pushes new data into pipe or buffer
    #doc.add_next_tick_callback(partial(buffer_or_pipe.send, data))
    #tornado.ioloop.IOLoop.instance().add_callback(partial(buffer_or_pipe.send, data))
    next_tick_callback = doc.add_next_tick_callback(partial(test_func,buffer_or_pipe,data,n))
    return next_tick_callback
    
def data_into_recent_hits_pipes(buffer_or_pipe_list, data,n):
    # pushes new data into pipe or buffer
    #doc.add_next_tick_callback(partial(buffer_or_pipe.send, data))
    #tornado.ioloop.IOLoop.instance().add_callback(partial(buffer_or_pipe.send, data))
    #print(len(data))
    next_tick_callback = doc.add_next_tick_callback(partial(fill_recent_hits_pipes,buffer_or_pipe_list,data,n))
    return next_tick_callback
    
def data_into_buffer_or_pipe_debug(buffer_or_pipe, data, n):
    # pushes new data into pipe or buffer
    #doc.add_next_tick_callback(partial(buffer_or_pipe.send, data))
    #tornado.ioloop.IOLoop.instance().add_callback(partial(buffer_or_pipe.send, data))
    next_tick_callback = doc.add_next_tick_callback(partial(test_func_debug,buffer_or_pipe,data, n))
    return next_tick_callback

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
    #print(data)  
    buffer_or_pipe.send(data)      
# plot tools functions
def largeData_line_plot(pipe_or_buffer, width=1500, height=400,ylim=(-500, 40),xlim=(start_tof,start_tof+N_datapts), xlabel="index", ylabel="TOF signal", cmap = ['blue'], title=None):
    TOF_dmap = hv.DynamicMap(hv.Curve, streams=[pipe_or_buffer])
    TOF_dmap_opt = datashade(TOF_dmap, streams=[PlotSize, RangeXY], dynamic=True, cmap = cmap)
    return hv_to_bokeh_obj( TOF_dmap_opt.opts(width=width,height=height,ylim=ylim,xlim=xlim, xlabel=xlabel, ylabel=ylabel, title = title) )
    
def smallData_line_plot(pipe_or_buffer, width=1500, height=400,ylim=(-500, 40),xlim=(start_tof,start_tof+N_datapts), xlabel="index", ylabel="TOF signal", title=None):
    TOF_dmap = hv.DynamicMap(hv.Curve, streams=[pipe_or_buffer]).redim.range().opts( norm=dict(framewise=True) ) #.redim.range().opts( norm=dict(framewise=True) ) makes x and y lim dynamic
    return hv_to_bokeh_obj( TOF_dmap.opts(width=width,height=height,ylim=ylim,xlim=xlim, xlabel=xlabel, ylabel=ylabel, title = title))

def pnCCDData_plot(pipe_or_buffer, width=500, height=500,ylim=(-0.5,0.5),xlim=(-0.5,0.5), title=None):
    TOF_dmap = hv.DynamicMap(hv.Image, streams=[pipe_or_buffer])
    #TOF_dmap_opt = rasterize(TOF_dmap) 
    TOF_dmap_opt = TOF_dmap
    #TOF_dmap_opt = datashade(TOF_dmap, streams=[PlotSize, RangeXY], dynamic=True)
    return hv_to_bokeh_obj( TOF_dmap_opt.opts(width=width,height=height,ylim=ylim,xlim=xlim, title = title, colorbar = True) )

def start_stop_dataThread():
    global makeBigData_stop
    if not makeBigData_stop:
        makeBigData_stop = True
    else:
        thread.start()
    
# Data buffers for live stream


_SQSbuffer__TOF_integral = online.DataBuffer(100)
_SQSbuffer__TOF_avg = online.DataBuffer(100)
_SQSbuffer__TOF_hit_trace = online.DataBuffer(1)
_SQSbuffer__TOF_hits = online.DataBuffer(1000)
_SQSbuffer__GMD_history = online.DataBuffer(100)
#_SQSbuffer__pnCCD_integral = online.DataBuffer(100)
_SQSbuffer__TOF_hits = online.DataBuffer(10)
#for k in range(5):
#    _SQSbuffer__pnCCD_hits(imresize(np.zeros(shape=(1024,1024)),img_downscale))
_SQSbuffer__counter = online.DataBuffer(100)
print("...2")

# Data pipes and buffers for plots
## pipes provide a full update of data to the underlying object eg. plot
## buffers add only a single value to the plot and may kick one out when number of elements in the buffer has reached the length/size of the buffer
_pipe__TOF_single = Pipe(data=[])
_pipe__TOF_avg = Pipe(data=[])
#_buffer__TOF_integral = Buffer(pd.DataFrame({'x':[],'y':[]}, columns=['x','y']), length=100, index=False)
_pipe__TOF_integral = Pipe(data=[])
#_pipe__pnCCD_single = Pipe(data=[])
#_pipe__pnCCD_integral = Pipe(data=[])
_pipe__GMD_history = Pipe(data=[])
#_pipe__pnCCD_hits_list = list()
#for i in range(5):
#    _pipe__pnCCD_hits_list.append(Pipe(data=[]))
   
# SETUP PLOTS
print("...3")
# example for coupled plots
#         layout = hv.Layout(largeData_line_plot(_pipe__TOF_single, title="TOF single shots - LIVE") + largeData_line_plot(_pipe__TOF_single, title="TOF single shots - LIVE 2", cmap=['red'])).cols(1)
## TOF
bokeh_live_tof =  largeData_line_plot(_pipe__TOF_single, title="TOF single shots - LIVE", width = 1000, height=500) 
bokeh_avg_tof =  largeData_line_plot(_pipe__TOF_avg, title="TOF runnign avg", width = 1000, height=500) 

bokeh_buffer_tof_integral = smallData_line_plot(_pipe__TOF_integral, title="TOF trace full range integral (absolute)", xlim=(None,None), ylim=(0, None), width = 800, height = 250)
## pnCCD
#bokeh_live_pnCCD =  pnCCDData_plot(_pipe__pnCCD_single, title="pnCCD single shots - LIVE", width = 500, height =500) 
#bokeh_buffer_pnCCD_integral = smallData_line_plot(_pipe__pnCCD_integral, title="pnCCD single shots integral", xlim=(None,None), ylim=(0, None), width = 500, height = 250)
#bokeh_hits_pnCCD_list = list()
#for i in range(len(_pipe__pnCCD_hits_list)):
#    bokeh_hits_pnCCD_list.append(pnCCDData_plot(_pipe__pnCCD_hits_list[i], title="pnCCD Most Recent Hits "+str(i), width=370, height=300))
## GMD
bokeh_buffer_gmd_history = smallData_line_plot(_pipe__GMD_history, title="pulseE last 1000 Trains", xlim=(None,None), ylim=(0, None), width = 400, height =250)

## SET UP Additional Widgets
bokeh_button_StartStop = Button(label = "Start / Stop", button_type="success")
bokeh_button_StartStop.on_click(start_stop_dataThread)
# SET UP BOKEH LAYOUT
#
#bokeh_row_1 = row(bokeh_live_pnCCD,bokeh_live_tof,column(bokeh_buffer_tof_integral,bokeh_buffer_gmd_history),bokeh_buffer_pnCCD_integral)
#bokeh_row_2 = row(bokeh_hits_pnCCD_list[0],bokeh_hits_pnCCD_list[1],bokeh_hits_pnCCD_list[2],bokeh_hits_pnCCD_list[3],bokeh_hits_pnCCD_list[4])
#bokeh_row_2 = row(bokeh_hits_pnCCD_list[0],bokeh_hits_pnCCD_list[1])
bokeh_row_1 = row(bokeh_live_tof,bokeh_avg_tof)
bokeh_row_2 = row(bokeh_buffer_tof_integral,bokeh_buffer_gmd_history)
bokeh_row_interact  = bokeh_button_StartStop
bokeh_layout = column(bokeh_row_1,bokeh_row_2, bokeh_row_interact)
print("...4")
# add bokeh layout to current doc
doc.add_root(bokeh_layout)
print("...5")
# Start Thread for Handling of the Live Data Strem
thread = Thread(target=makeBigData)
thread.start()
