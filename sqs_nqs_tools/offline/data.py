import numpy as np
import matplotlib.pyplot as plt
import karabo_data as kd

from . import access

raw_dir = '/gpfs/exfel/exp/SQS/201802/p002195/raw/'

def getTOF( runNumber, path=raw_dir, tofrange=(260000,285000), 
              dirspec='SQS_DIGITIZER_UTC1/ADC/1:network', 
              elementspec='digitizers.channel_1_A.raw.samples', 
              correctionRange=(400000,400032) ):
    # note renamed from getRunTOF
    '''
    gets TOF data for a given run 
        inputs 
            runNumber = number of run of interest
            path = path for data; defined at the top
        outputs
            pixels = 
            tofdata 
            trainIds

    '''
    run = runFormat( runNumber )
    runData = kd.RunDirectory(path+run)
    
    data = access.getData(access.runDir( runNumber , path=path), dirspec, elementspec)
    
    pixels = np.arange(tofrange[0],tofrange[1])
    
    correction = np.mean( np.asarray(data)[ : , correctionRange[0]:correctionRange[1] ], 0)
    corrpixels = np.arange(correctionRange[0],correctionRange[1])
    
    #tofdata=correctTOF(np.asarray(data)[ : , tofrange[0]:tofrange[1] ], pixels, correction, corrpixels)
    tofdata = np.asarray(data)[ : , tofrange[0]:tofrange[1] ]
    trainIds = np.asarray(data.trainId)
    return trainIds, tofdata, pixels

def getPulseEnergies( run , path=raw_dir , devicePath='SA3_XTD10_XGM/XGM/DOOCS:output', dataPath='data.intensityTD'):
    '''
        Returns pulse energy
        BE WARY OF THIS FUNCTION!!!! Might not return true PE depending on train settings.
    '''
    print('BE WARY OF THIS FUNCTION!!!! Might not return true PE depending on train settings.')
    
    data = access.getData(access.runDir( run , path=path), devicePath, dataPath)
    dataArray = np.asarray( data )
    PID = np.argmin( np.abs( dataArray[0,:]-1 ) )
    
    trainIds = np.asarray(data.trainId)
    return trainIds, np.asarray(data[:,PID-1])

def getChamberHeight( run , path=raw_dir , devicePath='SQS_AQS_MOV/MOTOR/Y_DOWNSTR', dataPath='actualPosition.value' ):
    
    data = access.getData(access.runDir( run , path=path), devicePath, dataPath)   
     
    trainIds = np.asarray(data.trainId)
    return trainIds, np.asarray(data)
    
def getSrcValveDelay( run , path=raw_dir , devicePath='SQS_NQS_CRSC/TSYS/PARKER_TRIGGER', dataPath='actualDelay.value' ):
    # gives delay of cluster source valve 
    
    data = access.getData(access.runDir( run , path=path), devicePath, dataPath)  
    
    trainIds = np.asarray(data.trainId)
    return trainIds, np.asarray(data)

