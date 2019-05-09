import xfelmay2019 as xfel
import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
import karabo_bridge as kb
import karabo_data as kd

def correlationPlots(run, Path, roi, offset = 0):
    '''
    outputs a scatter plot correlating FEL pulse intensity to light peak
    inputs
        run = run number of interest
        Path = path to data
        roi = region of interest in TOF for integration
        offset = offset for +/- 1 error
    returns the correlation number and scatter plot

    '''
    runf=xfel.runFormat(run)
    runData = kd.RunDirectory(Path+runf)

    pixels, tofs, trainIds = xfel.getRunTOF( run, Path, tofrange=(265000,285000) )
    pulse_E = np.asarray(runData.get_array('SA3_XTD10_XGM/XGM/DOOCS:output','data.intensityTD' ))

    integratedROIs = []
    pulseEnergies = []
    for ind, elem in enumerate(trainIds):

        train_pos=np.where(trainIds==elem)[0][0]

        temp_E=pulse_E[1,:]
        pos=max(enumerate(temp_E), key=(lambda a: a[1]))
        run_E=pulse_E[:,pos[0]]

        train_E = run_E[train_pos]
        pulseEnergies.append(train_E + offset)
        integratedROIs.append(np.sum((tofs[train_pos])[(roi[0]<pixels)&(pixels<roi[1])]))
        
    plt.scatter(pulseEnergies, integratedROIs)
    plt.xlabel('pulse energy')
    plt.ylabel('integrated ROI from TOF')
    
    corr = np.corrcoef(pulseEnergies, integratedROIs)
    
    return
