'''
module providing functions for data access. This should extent to files beeing automatically served or hdf5's accessed.

Second part of the file contains access functions to the data within a stream without altering the data. Analysis functions, which are returning data, that was not directly saved within the stream should go into `analysis.py`. Complicated analysis which requires multiple functions, just add another python file to this repository.

Stephan Kuschel, 2019

Everything takes in a dict of data being passed down the line

SO far: working (i think) stream for: 
    image&tof function
    tof function
    pulseEnergy function
    arbitrary data
If this does actually work, I'll make a nicer interface here
'''
from . import generatorpipeline as gp
from ..experimentDefaults import defaultConf
import numpy as np


# ---- Access the data on disk or network ----


#this opens the datastream
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
        yield {'data':ret[0], 'meta':ret[1]} #it comes out as a dict so the we have a consistent datastream



# ---- Access specific data from the stream ----


#@gp.pipeline_parallel()  #does not work due to pickling error of the undecorated function
def _getTof(d, idx_range=defaultConf['tofRange'], tofDev=defaultConf['tofDevice'], baselineTo=defaultConf['tofBaseEnd']):
    data = d['data']
    meta = d['meta']
    if tofDev in data:
        tofraw = data[tofDev]['digitizers.channel_1_A.raw.samples']
    else:
        print("Warning Device Not in Data - "+'tof'+"  ---> make some radnom tof data")
        tofraw = np.random.rand(1200000)
    tofcut = np.array(tofraw[idx_range[0]:idx_range[1]])
    

 #   if baselineTo > 0:
 #       d['tof'] = tofcut - np.mean(tofcut[:baselineTo])
 #   else:
 #       d['tof'] = tofcut

    #subtract channel offsets
    #subtract a baseline if we are using one
    nChan = defaultConf['tofChannels']
    if baselineTo > 0:
        for c in range(nChan):
            tofcut[c::nChan] = tofcut[c::nChan] - np.mean(tofcut[c:baselineTo:nChan])
        
    d['tof'] = (tofcut)

    return d
getTof = gp.pipeline_parallel(defaultConf['dataWorkers'])(_getTof)  # this works



def _getPulseEnergy(d, energyDev=defaultConf['pulseEDevice']):
    data = d['data']
    meta = d['meta']
    d['pulseEnergy'] = data[energyDev]['pulseEnergy.crossUsed.value'] 
    return d
getPulseEnergy = gp.pipeline_parallel(1)(_getPulseEnergy)  # this works



@gp.pipeline
def getSomeDetector(d, name='data', spec0='SQS_DPU_LIC/CAM/YAG_UPSTR:daqOutput', spec1='data.image.pixels', readFromMeta=False): ###should this even have a default?
    data = d['data']
    meta = d['meta']
    if not readFromMeta:
        try:
            d[name] = data[spec0][spec1]
        except:
            print("Warning Device Not in Data - "+name)
            d[name] = np.array([0])
    elif readFromMeta:
        try:
            d[name] = meta[spec0][spec1]
        except:
            print("Warning Device Not in Data - "+name)
            d[name] = np.array([0])
    return d

@gp.pipeline
def getSomePnCCD(d, name='data', spec0='SQS_DPU_LIC/CAM/YAG_UPSTR:daqOutput', spec1='data.image.pixels', readFromMeta=False): ###should this even have a default?
    data = d['data']
    meta = d['meta']
    if not readFromMeta:
        if spec0 in data:
            d[name] = data[spec0][spec1]
        else:
            print("Warning Device Not in Data - "+name+"  ---> make some radnom pnccd data")
            d[name] = (np.random.rand(1024,1024)*100).astype(np.float64).tobytes()
    elif readFromMeta:
        if spec0 in data:
            d[name] = meta[spec0][spec1]
        else:
            print("Warning Device Not in (meta) Data - "+name)
            d[name] = np.array([0])
    return d

@gp.pipeline
def getImage(d, imDev=defaultConf['imageDevice']):
    data = d['data']
    meta = d['meta']   
    d['image'] = data[imDev]['data.image.pixels']
    d['tid'] = meta[imDev]['timestamp.tid']
    return d

# --- scalar values: motor positions.... ---

@gp.pipeline
def tid(streamdata, imDev=defaultConf['imageDevice']):
    '''
    train id
    '''
    data, meta = streamdata
    ret = meta[imDev]['timestamp.tid'] 
    return ret

#@gp.pipeline
def _getImageandTof(d, tofDev=defaultConf['tofDevice'], idx_range=defaultConf['tofRange'], imDev=defaultConf['imageDevice'], baselineTo=defaultConf['tofBaseEnd']):
    data = d['data']
    meta = d['meta']
    
    tofraw = data[tofDev]['digitizers.channel_1_A.raw.samples']
    tofcut = np.array(tofraw[idx_range[0]:idx_range[1]])
    
    #subtract a baseline if we are using one
    if baselineTo > 0:
        d['tof'] = tofcut - np.mean(tofcut[:baselineTo])
    else:
        d['tof'] = tofcut

    d['image'] = data[imDev]['data.image.pixels']
    d['tid'] = tid = meta[imDev]['timestamp.tid']
    return d
getImageandTof = gp.pipeline_parallel(defaultConf['dataWorkers'])(_getImageandTof)  # this works
# --- scalar values: motor positions.... ---
