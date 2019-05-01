'''
Libraries for pulling and analyzing offline data

by Matthew Ware, Stephan Kuschel, Catherine Saladrigas
'''

# Import required libraries
import numpy as np

# Import karabo libraries
import karabo_bridge as kb
import karabo_data as kd

###################################################################################################
# TOF functions
###################################################################################################
def tofAverager( runData, nmax = 50 ):
    '''
    generates average of tofdata across nmax shots
    input:
        runData: run directory generated from karabo_data.RunDirectory(path+run)
        nmax: number of tof traces to average over from run
    output:
        averaged tof trace (np.array, float)
    '''
    tofsum = None
    isum = 0
    for tid, data in runData.trains():
    #     print("Processing train", tid)
        tofdata = data['SQS_DIGITIZER_UTC1/ADC/1:network']['digitizers.channel_1_A.raw.samples']
        if tofsum is None:
            tofsum = tofdata
            isum += 1
        else:
            tofsum += tofdata
            isum += 1
        if isum > nmax:
            break
    return tofsum/float(nmax)

def normalizedTOF( toftrace , downsampleRange=(268000,280000) , baselineFrom=-2000 ):
    '''
    input:
        toftrace: raw tof trace
        downsampleRange: (int,int) tuple giving range over which to downsmaple TOF
        baselineFrom: gives start index for calculating baseline average
    output:
        normalizedTOFTrace: puts tof trace in standard form for analysis
    '''
    # Reduce dimension of TOF to span desired range
    newtof = toftrace[downsampleRange[0]:downsampleRange[1]]
    N = newtof.size
    x = np.arange(N)

    # Substract mean of remaining TOF trace and take absolute value
    newtof_mean = np.mean( newtof[baselineFrom:] )
    return np.abs(newtof - newtof_mean)

from scipy.signal import find_peaks_cwt
def findTOFPeaks( toftrace ):
    '''
    input:
        toftrace: use normalized tof trace generated from normalizedTOF, numpy array of floats
    output:
        peak_positions: returns indexes of the TOF peaks
        peak_values: returns height of TOF peaks
    '''
    base_width = 200.
    # Find indexes of inds
    zf = find_peaks_cwt(toftrace, [base_width, base_width/2., base_width/4.])
    
    # Create averaging zones around peaks
    zguess = np.zeros_like(zf).astype(float) # allocate space

    for ii,zfi in enumerate(zf):
        xlow = (np.round( zfi - base_width/2. )).astype(int)
        if xlow < 0:
            xlow = 0
        xhigh = (np.round( zfi + base_width/2. )).astype(int)
        if xhigh > toftrace.size:
            xhigh = toftrace.size
            
        zguess[ii] = np.max(toftrace[xlow:xhigh])
        
    return zf, zguess

def runFormat( runNumber ):
    return '/r{0:04d}'.format(runNumber)
