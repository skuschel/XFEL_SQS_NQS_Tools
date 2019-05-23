import numpy as np
import matplotlib.pyplot as plt
import karabo_data as kd

from . import access

raw_dir = '/gpfs/exfel/exp/SQS/201802/p002195/raw/'

def getPulseEnergies( run , path=raw_dir , devicePath='SA3_XTD10_XGM/XGM/DOOCS:output', dataPath='data.intensityTD'):
    '''
        Returns pulse energy
        BE WARY OF THIS FUNCTION!!!! Might not return true PE depending on train settings.
    '''
    print('BE WARY OF THIS FUNCTION!!!! Might not return true PE depending on train settings.')
    
    data = access.getData(access.runDir( run , path=path), devicePath, dataPath)
    dataArray = np.asarray( data )
    PID = np.argmin( np.abs( dataArray[0,:]-1 ) )
    
    
    return np.asarray(data.trainId), np.asarray(data[:,PID-1])

def getChamberHeight( run , path=raw_dir , devicePath='SQS_AQS_MOV/MOTOR/Y_DOWNSTR', dataPath='actualPosition.value' ):
    
    data = access.getData(access.runDir( run , path=path), devicePath, dataPath)    
    
    return np.asarray(data.trainId), np.asarray(data)
    
def getSrcValveDelay( run , path=raw_dir , devicePath='SQS_NQS_CRSC/TSYS/PARKER_TRIGGER', dataPath='actualDelay.value' ):
    # gives delay of cluster source valve 
    
    data = access.getData(access.runDir( run , path=path), devicePath, dataPath)  
    
    return np.asarray(data.trainId), np.asarray(data)
