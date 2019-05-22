'''
module for SIMPLE, single function data analysis.

COMPLICATED analysis which requires multiple functions, just add another python file to this repository.

'''

from . import *
import numpy as np
from scipy.signal import find_peaks_cwt





# ---- TOF peakfining and spectrum ----

def findTOFPeaks( toftrace ):
    '''
    input:
        toftrace: use normalized tof trace generated from normalizedTOF, numpy array of floats
    output:
        peak_positions: returns indexes of the TOF peaks
        peak_values: returns height of TOF peaks
    Watthew Ware, 2019
    '''
    toftrace = np.abs(toftrace)

    # Find indexes of inds
#    base_width = 200.
#    zf = find_peaks_cwt(toftrace, [base_width, base_width/2., base_width/4.])

    base_width = 100.
    zf = find_peaks_cwt(toftrace, [base_width])
    
    # Create averaging zones around peaks
    zguess = np.zeros_like(zf).astype(float) # allocate space

    for ii,zfi in enumerate(zf):
        xlow = (np.round( zfi - base_width/2. )).astype(int)
        if xlow < 0:
            xlow = 0
        xhigh = (np.round( zfi + base_width/2. )).astype(int)
        if xhigh > toftrace.size:
            xhigh = toftrace.size
            
        zguess[ii] = np.mean(toftrace[xlow:xhigh])
        
    return zf, zguess
