'''
module providing functions for data access. This should extent to files beeing automatically served or hdf5's accessed.

Second part of the file contains access functions to the data within a stream without altering the data. Analysis functions, which are returning data, that was not directly saved within the stream should go into `analysis.py`. Complicated analysis which requires multiple functions, just add another python file to this repository.

Stephan Kuschel, 2019
'''
from . import generatorpipeline as gp
import numpy as np


# ---- Access the data on disk or network ----


def servedata(host, type='REQ'):
    '''
    Generator for the online data stream.
    Input: 
        host: ip address of data stream
        type: ???
    Output:
        dictionary of values for current event
    '''
    from karabo_bridge import Client
    # Generate a client to serve the data
    c = Client(host, type)

    # Return the newest event in the datastream using an iterator construct
    for ret in c:
    	yield ret



# ---- Access specific data from the stream ----


#@gp.pipeline_parallel()  #does not work due to pickling error of the undecorated function
def _getTof(streamdata):
    data, meta = streamdata
    ret = data['SQS_DIGITIZER_UTC1/ADC/1:network']['digitizers.channel_1_A.raw.samples']
    return np.array(ret[262000:290000])
getTof = gp.pipeline_parallel(1)(_getTof)  # this works

def _getPulseEnergy(streamdata):
    data, meta = streamdata
    ret = data['SA3_XTD10_XGM/XGM/DOOCS']['pulseEnergy.crossUsed.value']
    return ret
getPulseEnergy = gp.pipeline_parallel(1)(_getPulseEnergy)  # this works


@gp.pipeline
def baselinedTOF(streamdata, downsampleRange=(268000,280000) , baselineFrom=-2000 ):
    '''
    input:
        streamdata
        downsampleRange: (int,int) tuple giving range over which to downsmaple TOF
        baselineFrom: gives start index for calculating baseline average
    output:
        normalizedTOFTrace: puts tof trace in standard form for analysis
    Matthew Ware, 2019
    '''
    data, meta = streamdata
    toftrace = data['SQS_DIGITIZER_UTC1/ADC/1:network']['digitizers.channel_1_A.raw.samples']
    # Reduce dimension of TOF to span desired range
    newtof = toftrace[downsampleRange[0]:downsampleRange[1]]
    N = newtof.size
    x = np.arange(N)

    # Substract mean of remaining TOF trace and take absolute value
    newtof_mean = np.mean( newtof[baselineFrom:] )
    return newtof - newtof_mean


# --- Image stuff ---

#@gp.pipeline
#def getImage(streamdata):
#    data, meta = streamdata
#    ret = data['SQS_DPU_LIC/CAM/YAG_UPSTR:output']['data.image.data']
#    tid = meta['SQS_DPU_LIC/CAM/YAG_UPSTR:output']['timestamp.tid']
#    return dict(image=ret, tid=tid)

#@gp.pipeline
#def getImage(streamdata):
#    data, meta = streamdata
#    ret = data['SQS_DPU_LIC/CAM/YAG_UPSTR']['data.image.data']
#    tid = meta['SQS_DPU_LIC/CAM/YAG_UPSTR']['timestamp.tid']
#    return dict(image=ret, tid=tid)

def getSomeDetector(streamdata, spec0='SQS_DPU_LIC/CAM/YAG_UPSTR:daqOutput', spec1='data.image.pixels'):
    data, meta = streamdata
    ret = data[spec0][spec1]
    return ret

@gp.pipeline
def getImage(streamdata):
    data, meta = streamdata
#    ret = data['SQS_DPU_LIC/CAM/YAG_UPSTR:daqOutput']['data.image.data']
    ret = data['SQS_DPU_LIC/CAM/YAG_UPSTR:output']['data.image.data']
    tid = meta['SQS_DPU_LIC/CAM/YAG_UPSTR:output']['timestamp.tid']
#    ret = data['SQS_AQS_VMIS/CAM/PHSCICAM_MASTER:output']['data.image.data']
#    tid = meta['SQS_AQS_VMIS/CAM/PHSCICAM_MASTER:output']['timestamp.tid']
#    ret = data['SQS_AQS_VMIS/CAM/PHSCICAM_SLAVE:output']['data.image.data']
#    tid = meta['SQS_AQS_VMIS/CAM/PHSCICAM_SLAVE:output']['timestamp.tid']
    return dict(image=ret, tid=tid)


# --- scalar values: motor positions.... ---

@gp.pipeline
def tid(streamdata):
    '''
    train id
    '''
    data, meta = streamdata
    ret = meta['SQS_DPU_LIC/CAM/YAG_UPSTR:output']['timestamp.tid']
    return ret

@gp.pipeline
def getImageandTof(streamdata):
    data, meta = streamdata
#    ret = data['SQS_DPU_LIC/CAM/YAG_UPSTR:daqOutput']['data.image.data']
    ret = data['SQS_DPU_LIC/CAM/YAG_UPSTR:output']['data.image.data']
    tid = meta['SQS_DPU_LIC/CAM/YAG_UPSTR:output']['timestamp.tid']
#    ret = data['SQS_AQS_VMIS/CAM/PHSCICAM_MASTER:output']['data.image.data']
#    tid = meta['SQS_AQS_VMIS/CAM/PHSCICAM_MASTER:output']['timestamp.tid']
#    ret = data['SQS_AQS_VMIS/CAM/PHSCICAM_SLAVE:output']['data.image.data']
#    tid = meta['SQS_AQS_VMIS/CAM/PHSCICAM_SLAVE:output']['timestamp.tid']
    tofraw = data['SQS_DIGITIZER_UTC1/ADC/1:network']['digitizers.channel_1_A.raw.samples']
    tofcut = np.array(tofraw[262000:290000])
    return dict(image=ret, tid=tid, tof=tofcut)

# --- scalar values: motor positions.... ---
