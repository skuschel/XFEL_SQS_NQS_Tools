import xfelmay2019 as xfel
import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
import karabo_bridge as kb
import karabo_data as kd

def correlationPlots(run, Path, roi1, offset):
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
    scatImagesini = np.asarray(runData.get_array('SQS_DPU_LIC/CAM/YAG_UPSTR:daqOutput', 'data.image.pixels'))
    
    integratedROI1s = []

    pulseEnergies = []
    if offset > 0:
        for ind, elem in enumerate(trainIds[0:len(trainIds) - offset]):
            train_pos=np.where(trainIds==elem)[0][0]
            temp_E=pulse_E[1,:]
            pos=max(enumerate(temp_E), key=(lambda a: a[1]))
            run_E=pulse_E[:,pos[0]]
            train_E = run_E[train_pos+offset]
            pulseEnergies.append(train_E )

            integratedROI1s.append(np.sum((tofs[train_pos])[(roi1[0]<pixels)&(pixels<roi1[1])]))
    else:
            
        for ind, elem in enumerate(trainIds):

            train_pos=np.where(trainIds==elem)[0][0]
            #print (train_pos) 

            temp_E=pulse_E[1,:]
            #print (temp_E)

            pos=max(enumerate(temp_E), key=(lambda a: a[1]))
            run_E=pulse_E[:,pos[0]]
            #print (run_E)

            train_E = run_E[train_pos+offset]
            pulseEnergies.append(train_E )

            integratedROI1s.append(np.sum((tofs[train_pos])[(roi1[0]<pixels)&(pixels<roi1[1])]))

    
    plt.scatter(pulseEnergies, integratedROI1s)
    plt.xlabel('pulse energy')
    plt.ylabel('integrated ROI from TOF')
    
    return

