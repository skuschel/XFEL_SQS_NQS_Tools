import sqs_nqs_tools.online as online
import sqs_nqs_tools as tools
from sqs_nqs_tools.experimentDefaults import defaultConf

import numpy as np


## PARAMETERS
source = 'tcp://10.253.0.142:6666'  # LIVE
#~ source = 'tcp://127.0.0.1:8010' # emulated live

#### DataSourcesInStream
_inStream_pnCCD = True
_inStream_TOF = True
_inStream_XGM = True

#### TOF Properties
tof_prop = { 
            'N_datapts': 31000, # total number of TOF datapoints that are visualized
            'start_tof': 59000, # index of first TOF datapoint consideredend_tof = start_tof+N_datapts # index of last TOF datapoint considered
            'baseline_to': 1000 # index until which baseline (no signal) can be used to calculate the 0
            }
######## calculated tof properties
tof_prop['end_tof'] = tof_prop['start_tof'] + tof_prop['N_datapts']
tof_prop['x_tof'] = np.arange(tof_prop['start_tof'],tof_prop['end_tof']) # x-axis for tof data points


#### PNCCD Properties
pnCCD_prop = {
                'pnccd_crop_limits' : [0,1024,0,1024],
                'single_photon_adu' : 250,
                'hit_threshold_integral' : 3e5,
                'hit_threshold_combined_integral' : 1.6e5,
                'background_pnCCD__get' : True,
                'background_pnCCD__file' : 'background_pnCCD.npy',
                'background_max_pnCCD__get' : True,
                'background_max_pnCCD__file' : 'background_max_pnCCD.npy',
                'img_downscale' : 30
                }
######## calculated pnccd properties
pnCCD_prop['pnccd_dims'] = [pnCCD_prop['pnccd_crop_limits'][1]-pnCCD_prop['pnccd_crop_limits'][0],pnCCD_prop['pnccd_crop_limits'][3]-pnCCD_prop['pnccd_crop_limits'][2]]
if pnCCD_prop['background_pnCCD__get']:
    pnCCD_prop['background_pnCCD__data'] = np.load(pnCCD_prop['background_pnCCD__file'])
if pnCCD_prop['background_max_pnCCD__get']:
    pnCCD_prop['background_max_pnCCD__data'] = np.load(pnCCD_prop['background_max_pnCCD__file'])

def buildDataStreamPipeline():
    ds = online.servedata(source) 
    if _inStream_TOF:
        ds = pipeline_TOF(ds, tof_prop)
    if _inStream_pnCCD:
        ds = pipeline_pnCCD(ds, pnCCD_prop)
    if _inStream_XGM:
        ds = pipeline_XGM(ds)
    
    return ds

@online.pipeline
def pipeline_TOF(d, tof_prop):
    # Load
    d['tof_x'] = tof_prop['tof_x']
    d = online.getTof(d,idx_range=[tof_prop['start_tof'],tof_prop['end_tof']],baselineTo=tof_prop['baseline_to'])
    d = online.getSomeDetector(d, name='tid', spec0=defaultConf['tofDevice'], spec1='digitizers.trainId') #get current trainids from digitizer property
    # Process
    d['tof_integral'] = abs(np.sum(data['tof']))
    d['tof_height'] = abs(np.min(data['tof']))
    
    return d

@online.pipeline    
def pipeline_pnCCD(d, pnCCD_prop):
    # Load
    d = online.getSomePnCCD(d, name='pnCCD', spec0='SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output', spec1='data.image')
    # Process Full Image
    d['pnCCD'] = np.squeeze(d['pnCCD'])
    d['pnCCD_hit_find'] = d['pnCCD']
    if pnCCD_prop['background_pnCCD__get']:
        d['pnCCD'] = d['pnCCD'] - pnCCD_prop['background_pnCCD__data']
    if pnCCD_prop['background_max_pnCCD__get']:
        d['pnCCD_hit_find'] = d['pnCCD_hit_find'] - pnCCD_prop['background_max_pnCCD__data']
        d['pnCCD_hit_find'][d['pnCCD_hit_find']<0]=0
    d['pnCCD_full'] = d['pnCCD']
    d['pnCCD_small'] = d['pnCCD'][256:768,256:768]
    d['pnCCD'] = d['pnCCD'][pnCCD_prop['pnccd_crop_limits'][0]:pnCCD_prop['pnccd_crop_limits'][1],pnCCD_prop['pnccd_crop_limits'][2]:pnCCD_prop['pnccd_crop_limits'][3]]
    # prep array for log plotting
    d['pnCCD_plot'] = d['pnccd'].copy()
    d['pnCCD_plot'][d['pnCCD_plot']<1] = 1
    # integrals
    d['pnCCD_integral'] = np.sum(data['pnCCD'])
    d['pnCCD_integral_hitfind'] = np.sum(data['pnCCD_hit_find'])
    
    return d

@online.pipeline    
def pipeline_XGM(d):
    d = online.getSomeDetector(d, name='gmd', spec0='SA3_XTD10_XGM/XGM/DOOCS:output', spec1='data.intensitySa3TD')
    d['gmd_0'] = data['gmd'][0]
    return d
